quick_reports = {
    # Artifact Type
    "UserStory": {
        
        # Columns to appear in Rally export. Note that some attributes are returned as objects (ex: Feature)
        # The artifact must be fetched on its own, then further attributes must be included as Artifact.Attribute to appear in the report.
        # A full list of artifacts and attributes can be found in the pyral documentation

        # The query_custom field should be used to customize parameters that can be changed by the user.

        # Queries are written as lambda functions (lambda data: data) to filter over dataframes returned from Rally API calls.
        # Some basic Python knowledge is needed to write your own custom queries. Fields are case-sensitive and referenced by data['field_name'].
        
        "headers": ["Feature", "Feature.Name", "FormattedID", "Name", "Owner", "Tags", "Milestones", "PlanEstimate", "c_AcceptanceCriteria", "Iteration", "ScheduleState", "c_AgencyKanban", "Blocked"],
        "custom_reports": {
            # Find user stories that have missing iteration, plan estimate, or acceptance criteria
            "user_story_default": {
                "headers": ["Feature", "Feature.Name", "FormattedID", "Name", "Owner", "Tags", "Milestones", "PlanEstimate", "c_AcceptanceCriteria", "Iteration", "ScheduleState", "c_AgencyKanban", "Blocked"],
                "query_custom": ["Milestones.Name = \"$\""],
                "query" : lambda data: (data["ScheduleState"] != "Idea" and data["Blocked"] != True and not data["Name"].startswith("Integration")) and ((data["PlanEstimate"] is None or data["AcceptanceCriteria"] is None or data["Iteration"] is None) or (data["ScheduleState"] != "Defined" and ("PO Signed Off" not in data["Tags"])))
            },
            "po_signed_off": {
                "headers": ["Feature", "Feature.Name", "FormattedID", "Name", "Owner", "Tags", "Milestones", "PlanEstimate", "AcceptanceCriteria", "Iteration", "ScheduleState", "AgencyKanban", "Blocked"],
                "query_custom": ["Milestones.Name = \"$\""],
                "query" : lambda data: data
            },
            "testcases": {
                "headers": ["Feature", "Feature.Name", "FormattedID", "Name", "Owner", "Tags", "Milestones", "PlanEstimate", "AcceptanceCriteria", "Iteration", "ScheduleState", "AgencyKanban", "Blocked", "TestCaseCount", "PassingTestCaseCount"],
                "query_custom": ["Milestones.Name = \"$\"", "Feature.FormattedID = $"],
                "query": lambda data: data
            }
        }
    },
    "Defect": {
        "headers": ['FormattedID', 'Name', 'Priority', 'State', 'SubmittedBy', 'Owner', 'Blocked', 'LastUpdateDate', 'CreationDate', 'Aging', 'Range'],
        "custom_reports": {
            "report1": {
                "headers": ['FormattedID', 'Name', 'Priority', 'State', 'SubmittedBy', 'ProjectPhase', 'Release', 'Owner', 'Blocked', 'LastUpdateDate', 'CreationDate', 'Aging', 'Range'],
                "query_custom": ["Release.Name = \"$\"", "ProjectPhase != \"$\""],
                "query" : lambda data: data["State"] != "Closed"
            }
        }

    }

}
