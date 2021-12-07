from jira import JIRA
import pprint
import time
from appscript import app, k
import jira
import keyring
from pprint import pprint
import re

def issue_to_dict(issue):
    dict = {}
    dict["key"]    = issue.key
    dict["type"]   = issue.fields.issuetype.name
    dict["status"] = issue.fields.status.name
    try:
        dict["priority"] = issue.fields.priority.name
    except AttributeError:
        pass
    try:
        dict["resolution"] = issue.fields.resolution.name
    except AttributeError:
        pass
    try:
        for version in issue.fields.fixVersions:
            if "fix_version" not in dict.keys():
                dict["fix_version"] = []
            dict["fix_version"].append(version.name)
    except AttributeError:
        pass
    try:
       if issue.fields.versions:
           for version in issue.fields.versions:
               if "affect_version" not in dict.keys():
                   dict["affect_version"] = []
               dict["affect_version"].append(version.name)
    except AttributeError:
        pass
       
    try:
        for component in issue.fields.components:
            if "components" not in dict.keys():
                dict["components"] = []
            dict["components"].append(component.name)
    except AttributeError:
        pass

    try:
        for label in issue.fields.labels:
            if "labels" not in dict.keys():
                dict["labels"] = []
            dict["labels"].append(label)
    except AttributeError:
        pass
    try:
        dict["revision_found"] = issue.fields.customfield_10287
    except AttributeError:
        pass
    try:
        for comment in issue.fields.comment.comments:
            if "comments" not in dict.keys():
                dict["comments"] = []
            dict["comments"].append({"user_id"  : comment.author.name,
                                    "email_id" : comment.author.emailAddress,
                                    "body"     : comment.body})
    except AttributeError:
        pass

    try:
        dict["reason_introduced"] = issue.fields.customfield_26631.value
    except:
        pass

    try:
        dict["time_remaining"] = issue.fields.timetracking.remainingEstimate
    except:
        pass

    dict["labels"] = []

    for label in issue.fields.labels:
        dict["labels"].append(label)

    dict["assignee"] = {"user_id"   : issue.fields.assignee.name,
                        "full_name" : issue.fields.assignee.displayName,
                        "email_id"  : issue.fields.assignee.emailAddress}
    dict["reporter"] = {"user_id"   : issue.fields.reporter.name,
                        "full_name" : issue.fields.reporter.displayName,
                        "email_id"  : issue.fields.reporter.emailAddress}
    
    dict["summary"] = issue.fields.summary
    return(dict)

def get_all_open_actions(user_ids,project):
    user_name = keyring.get_password("system","usr")
    jira = JIRA(options={'server':"https://jira.arm.com/"},basic_auth=(user_name,keyring.get_password("system",user_name)))
    assignee = "("
    for user_id in user_ids:
        index = user_ids.index(user_id) + 1
        assignee += f"(assignee = {user_id})"
        if index != len(user_ids):
            assignee += " OR "
    assignee += ")"
    jira_issues = jira.search_issues(f"{assignee} AND Resolution = Unresolved AND Type = Action AND project = {project}",maxResults=1000)
    issues = []
    if jira_issues.total > 1000:
        return((True,None))
    for issue in jira_issues:
        issues.append(issue_to_dict(issue))
    return(False,issues)

def get_all_open_bugs(user_ids,project):
    user_name = keyring.get_password("system","usr")
    jira = JIRA(options={'server':"https://jira.arm.com/"},basic_auth=(user_name,keyring.get_password("system",user_name)))
    assignee = "("
    for user_id in user_ids:
        index = user_ids.index(user_id) + 1
        assignee += f"(assignee = {user_id})"
        if index != len(user_ids):
            assignee += " OR "
    assignee += ")"
    jira_issues = jira.search_issues(f"{assignee} AND Resolution = Unresolved AND Type = Bug AND project = {project}",maxResults=1000)
    issues = []
    if jira_issues.total > 1000:
        return((True,None))
    for issue in jira_issues:
        issues.append(issue_to_dict(issue))
    return(False,issues)  

def get_all_open_tasks(user_ids,project):
    user_name = keyring.get_password("system","usr")
    jira = JIRA(options={'server':"https://jira.arm.com/"},basic_auth=(user_name,keyring.get_password("system",user_name)))
    assignee = "("
    for user_id in user_ids:
        index = user_ids.index(user_id) + 1
        assignee += f"(assignee = {user_id})"
        if index != len(user_ids):
            assignee += " OR "
    assignee += ")"
    jira_issues = jira.search_issues(f"{assignee} AND Resolution = Unresolved AND Type = 'Scheduled Task' AND project = {project}",maxResults=1000)
    if jira_issues.total > 1000:
        return((True,None))
    issues = []
    for issue in jira_issues:
        issue = jira.issue(issue.key)
        issues.append(issue_to_dict(issue))
    return((False,issues)) 


def create_jira_info_content(sheet,open_actions,actions_jira_ids):
    mod_sheet = {}
    mod_sheet['sheet_name'] = sheet['sheet_name']
    mod_sheet['col_list'] = sheet ['col_list']
    mod_sheet['content'] = []
    for action in open_actions:

        link_jira = f'=HYPERLINK("https://jira.arm.com/browse/{action["key"]}","{action["key"]}")'
        content = {"JIRA ID"      : link_jira,
                   "Summary"      : action['summary'],
                   "Assignee"     : action['assignee']['user_id']}
        fix_version_str = ""
        if "fix_version" in action.keys():
            for version in action['fix_version']:
                index = action['fix_version'].index(version) + 1
                fix_version_str += version
                if index != len(action['fix_version']):
                    fix_version_str += ","
            content.update({"Fix Versions" : fix_version_str})
    
        if "time_remaining" in action.keys():
            content.update({"time_remaining":action['time_remaining']})

        if action['key'] in actions_jira_ids:
            index = actions_jira_ids.index(action['key'])
            content['Comments'] = sheet['content'][index]['Comments']
        else:
            content.update({"Comments" : ""})

        labels = ""
        for label in action["labels"]:
            labels += f" {label}"
        content.update({"Labels": labels})
        mod_sheet['content'].append(content)
    return(mod_sheet)

class JIRAUSER():

    # Has following fields
    #   user_id       : unix id of the user
    #   email_id      : email id of the user
    #   cc_email_id   : email_id of people to be put in cc
   
    def __init__(self,user_info={}):
        self.user_id = user_info.get("user_id","ragban01")
        self.email_id = user_info.get("email_id","raghavendra.bandimutt@arm.com")
        self.cc_email_id = []
        if "cc_email_id" in user_info.keys():
            for email_id in user_info["cc_email_id"]:
                self.cc_email_id.append(email_id)
        user_name = keyring.get_password("system","usr")
        self.jira = JIRA(options={'server':"https://jira.arm.com/"},basic_auth=(user_name,keyring.get_password("system",user_name)))
        self.issues = []

    ## Function gets all the open actions for a user 
    def get_all_open_actions(self):
        jira_issues = self.jira.search_issues(f"assignee = {self.user_id} AND Resolution = Unresolved AND Type = Action")
        self.issues = []
        for issue in jira_issues:
            self.issues.append(self.issue_to_dict(issue))
    

    ## Function which returns a HTML string which is list of all open actions with summary
    def get_all_open_actions_str(self):
        self.get_all_open_actions()
        if len(self.issues)>0:
            content = "<h2><u> Summary of all open actions </u></h2><br>"   
        else:
            content = ""
        for issue in self.issues:
            content += f'<u><a href="https://jira.arm.com/browse/{issue["key"]}"> {issue["key"]} </a> </u> : {issue["summary"]}<br>'
        return(content)

    ## Function gets all the open bugs for a user
    def get_all_open_bugs(self):
        jira_issues = self.jira.search_issues(f"assignee = {self.user_id} AND Resolution = Unresolved AND Type = Bug")
        self.issues = []
        for issue in jira_issues:
            self.issues.append(self.issue_to_dict(issue))

    ## Function which returns a HTML string which is list of all open bugs with summary
    def get_all_open_bugs_str(self):
        self.get_all_open_bugs()
        if len(self.issues) > 0:
            content = "<h2><u> Summary of all open bugs </u></h2><br>" 
        else:
            content = ""
        for issue in self.issues:
            content += f'<u><a href="https://jira.arm.com/browse/{issue["key"]}"> {issue["key"]} </a> </u> : {issue["summary"]}<br>'
        return(content)

    ## Functions which returns a HTML string which is list of all open Jiras without fixrevisions
    def get_all_issues_without_fix_versions(self,project):
        jira_issues = self.jira.search_issues(f"(assignee = {self.user_id} or reporter={self.user_id}) AND Resolution = Unresolved AND project = {project}")
        self.issues = []
        for issue in jira_issues:
            local_issue_dict = self.issue_to_dict(issue)
            if "fix_version" not in local_issue_dict.keys():
                self.issues.append(local_issue_dict)

        if len(self.issues) > 0:
            content = "<h2><u> Summary of all open Jiras without fix revisions </u></h2><br>" 
        else:
            content = ""
        for issue in self.issues:
            content += f'<u><a href="https://jira.arm.com/browse/{issue["key"]}"> {issue["key"]} </a> </u> : {issue["summary"]}<br>'
        return(content)

    ## Function gets all the open tasks for a user
    def get_all_open_task(self):
        jira_issues = self.jira.search_issues(f"assignee = {self.user_id} AND Resolution = Unresolved AND Type = 'Scheduled Task' AND project = PJ02932")
        self.issues = []
        for issue in jira_issues:
            self.issues.append(self.issue_to_dict(issue))

    ## Function which returns a HTML string which is list of all open tasks with summary
    def get_all_open_task_str(self):
        self.get_all_open_task()
        if len(self.issues) > 0:
            content = "<h2><u> Summary of all open tasks </u></h2><br>" 
        else:
            content = ""
        for issue in self.issues:
            content += f'<u><a href="https://jira.arm.com/browse/{issue["key"]}"> {issue["key"]} </a> </u> : {issue["summary"]}<br>'
        return(content)

    # Function to get all task of reporter which is fixed but not closed
    def get_all_fixed_not_closed(self,project):
        jira_issues = self.jira.search_issues(f"reporter = {self.user_id} AND Resolution = Fixed AND status = Resolved AND project = {project}")
        self.issues = []
        for issue in jira_issues:
            self.issues.append(self.issue_to_dict(issue))
        if len(self.issues) > 0:
            content = "<h2><u> Summary of all Jiras that are resolved but not closed </u></h2><br>"
        else:
            content = ""
        for issue in self.issues:
            content += f'<u><a href="https://jira.arm.com/browse/{issue["key"]}"> {issue["key"]} </a> </u> : {issue["summary"]}<br>'
        return(content)    

    # Function to get all task which is fixed but no reason introduced
    def get_all_fixed_no_reason(self,project):
        jira_issues = self.jira.search_issues(f"(reporter = {self.user_id} or assignee = {self.user_id}) AND Resolution = Fixed AND status = Resolved AND project = {project}")
        self.issues = []
        for issue in jira_issues:
            issue_dict = self.issue_to_dict(issue)
            if "reason_introduced" not in issue_dict.keys():
                self.issues.append(self.issue_to_dict(issue))
        if len(self.issues) > 0:
            content = "<h2><u> Summary of all Jiras that are resolved but no reason introduced </u></h2><br>"
        else:
            content = ""
        for issue in self.issues:
            content += f'<u><a href="https://jira.arm.com/browse/{issue["key"]}"> {issue["key"]} </a> </u> : {issue["summary"]}<br>'
        return(content)        
        
        
    def get_all_issues(self,search_criteria):
        jira_issues = self.jira.search_issues(search_criteria)
        self.issues = []
        for issue in jira_issues:
            self.issues.append(self.issue_to_dict(issue))

    def issue_to_dict(self,issue):
        dict = {}
        dict["key"]    = issue.key
        dict["type"]   = issue.fields.issuetype.name
        dict["status"] = issue.fields.status.name
        try:
            dict["priority"] = issue.fields.priority.name
        except AttributeError:
            pass


        try:
            dict["resolution"] = issue.fields.resolution.name
        except AttributeError:
            pass

        try:
            for version in issue.fields.fixVersions:
                if "fix_version" not in dict.keys():
                    dict["fix_version"] = []
                dict["fix_version"].append(version.name)
        except AttributeError:
            pass

        try:
           if issue.fields.versions:
               for version in issue.fields.versions:
                   if "affect_version" not in dict.keys():
                       dict["affect_version"] = []
                   dict["affect_version"].append(version.name)
        except AttributeError:
            pass
           

        try:
            for component in issue.fields.components:
                if "components" not in dict.keys():
                    dict["components"] = []
                dict["components"].append(component.name)
        except AttributeError:
            pass

    
        try:
            for label in issue.fields.labels:
                if "labels" not in dict.keys():
                    dict["labels"] = []
                dict["labels"].append(label)
        except AttributeError:
            pass

        try:
            dict["revision_found"] = issue.fields.customfield_10287
        except AttributeError:
            pass

        try:
            for comment in issue.fields.comment.comments:
                if "comments" not in dict.keys():
                    dict["comments"] = []
                dict["comments"].append({"user_id"  : comment.author.name,
                                        "email_id" : comment.author.emailAddress,
                                        "body"     : comment.body})
        except AttributeError:
            pass

        try:
            dict["reason_introduced"] = issue.fields.customfield_26631.value
        except:
            pass

        dict["assignee"] = {"user_id"   : issue.fields.assignee.name,
                            "full_name" : issue.fields.assignee.displayName,
                            "email_id"  : issue.fields.assignee.emailAddress}

        dict["reporter"] = {"user_id"   : issue.fields.reporter.name,
                            "full_name" : issue.fields.reporter.displayName,
                            "email_id"  : issue.fields.reporter.emailAddress}
        
        dict["summary"] = issue.fields.summary
        return(dict)

    
    def send_msg_to_user(self,user_msg):
        """send_msg_to_user : is used to send email to the user
            supports input argument user_msg which is a dictonary
                subject : Subject of the email
                content : Body of the email
        """
        outlook = app('Microsoft Outlook')
        # Create new outlook message with HTML content
        msg = outlook.make(
                new=k.outgoing_message,
                with_properties={
                    k.subject: user_msg["subject"],
                    #k.plain_text_content: 'Test email body'})
                    k.content: user_msg["content"]})

        msg.make(
            new=k.recipient,
            with_properties={
               k.email_address: {
               k.name: self.user_id,
               k.address: self.email_id}})
        

        for email_id in self.cc_email_id:
            print(f"cc {email_id}")
            msg.make(
                new=k.cc_recipient,
                with_properties={
                    k.email_address: {
                    k.name: self.user_id,
                    k.address: email_id}})

        msg.send()
        









# issue1 = jira.issue("PJ02932-15722")
# issue2 = jira.issue("PJ02932-12959")
# issue3 = jira.issue("PJ02932-15774")
# issue4 = jira.issue("PJ02932-14511")

#content = f"'{issue1.key} : https://jira.arm.com/browse/{issue1.key}'"
#print(content)
#
#os.system(f"mail -s 'First email1' raghavendra.bandimutt@arm.com <<< {content}")

#pprint.pprint(vars(issue1))
#pprint.pprint(vars(issue2))
#pprint.pprint(vars(issue3))
#pprint.pprint(vars(issue4))
# Jira number = issue.key
# Issue type = issue.fields.issuetype.name
# status = issue.fields.status.name
# priorty = issue.fields.priority.name
# resolution = issue.fields.resolution.name
# fixversions = issue.fields.fixVersions[0].name
# Affects verisons = issue.fields.versions[0].name
# components = issue.fields.components[0].name
# labels = issue.fields.labels[0]
# Revision found = issue.fields.customfield_10287
# Comments author = issue.fields.comment.comments[0].author.name
# comments of author = issue.fields.comment.comments[0].author.body
# assignee user name = issue.fields.assignee.name
# assignee full name = issue.fields.assignee.displayName
# assignee email id = issue.fields.assignee.emailAddress
# reporter user name = issue.fields.reporter.name
# reporter full name = issue.fields.reporter.displayName
# reporter email id = issue.fields.reporter.emailAddress

# print(issue3.fields.comment.comments[0].body)
#for issue in jira.search_issues("assignee = currentUser() AND resolution = Unresolved order by updated DESC"):
  #print(f"{issue.key}:{issue.fields.issuetype.name}:{issue.fields.status.name}:{issue.fields.priority.name}")

