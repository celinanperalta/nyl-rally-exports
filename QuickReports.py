quick_reports = {
    # Artifact Type
    "UserStory": {
        
        # Columns to appear in Rally export. Note that some attributes are returned as objects (ex: Feature)
        # The artifact must be fetched on its own, then further attributes must be included as Artifact.Attribute to appear in the report.
        # A full list of artifacts and attributes can be found in the pyral documentation
        
        "headers": ["Feature", "Feature.Name", "FormattedID", "Name", "Owner", "Tags", "Milestones", "PlanEstimate", "AcceptanceCriteria", "Iteration", "ScheduleState", "AgencyKanban", "Blocked"],
        "custom_reports": {
            # Find user stories that have missing iteration, plan estimate, or acceptance criteria
            "user_story_default": {
                "headers": ["Feature", "Feature.Name", "FormattedID", "Name", "Owner", "Tags", "Milestones", "PlanEstimate", "AcceptanceCriteria", "Iteration", "ScheduleState", "AgencyKanban", "Blocked"],
                "query_custom": ["Milestones.Name = \"$\""],
                "query": ["ScheduleState != Idea", "Blocked != True", "Name !contains Integration",
                          "PlanEstimate = null OR AcceptanceCriteria = null OR Iteration = null OR ScheduleState != Defined AND Tags.Name !contains \"PO Signed off\""]
                
            },
            #merge po sign off and missing criteria
            "po_signed_off": {
                "headers": ["Feature", "Feature.Name", "FormattedID", "Name", "Owner", "Tags", "Milestones", "PlanEstimate", "AcceptanceCriteria", "Iteration", "ScheduleState", "AgencyKanban", "Blocked"],
                "query_custom": ["Milestones.Name = \"$\""],
                "query": ["ScheduleState != Idea", "ScheduleState != Defined", "Blocked != True", "Tags.Name !contains \"PO Signed off\""],
            },
            "testcases": {
                "headers": ["Feature", "Feature.Name", "FormattedID", "Name", "Owner", "Tags", "Milestones", "PlanEstimate", "AcceptanceCriteria", "Iteration", "ScheduleState", "AgencyKanban", "Blocked", "TestCaseCount", "PassingTestCaseCount"],
                "query_custom": ["Milestones.Name = \"$\"", "Feature.FormattedID = $"],
                "query": []
            }
        }
    },
    "Defect": {
        "headers": ['FormattedID', 'Name', 'Priority', 'State', 'SubmittedBy', 'Owner', 'Blocked', 'LastUpdateDate', 'CreationDate', 'Aging', 'Range'],
        "custom_reports": {
            "report1": {
                "headers": ['FormattedID', 'Name', 'Priority', 'State', 'SubmittedBy', 'Owner', 'Blocked', 'LastUpdateDate', 'CreationDate', 'Aging', 'Range'],
                "query_custom": ["Release.Name = \"$\"", "ProjectPhase != \"$\""],
                "query" : ["State != Closed"]
            }
        }

    }

}
