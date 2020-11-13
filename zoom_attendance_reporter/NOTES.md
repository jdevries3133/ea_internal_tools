# Flow

## Get the user ready / providing instructions.

1. User can view sample report to see what they're getting.
2. Link to zoom help link on where to find the reports.
3. Screenshot highlighting the boxes they must check in zoom
    - limit to unique users
    - include meeting information
4. FAQ (separate page)
    - Will this work if I meet with different groups of students with the same meeting? (yes)
    - Is this safe? (explain it is & why)
    - How are zoom names matched to real names?

## User does the thing:

1. File upload form; let them shift-click to upload multiple.
2. Go through a round of name matching as per below.
3. Return thicc excel file, colored and with multiple tabs.
4. Explain that excel can be uploaded to drive for viewing if they don't have
    excel.

## Name Matching

Let the users generate a library of whacky zoom names mapped to their real
name.

**Flow**

1. User submits uploaded galleries.
2. Backend parses all.
3. An instance of UnknownZoomName model is saved to the database with the
    real_name field blank.
4. User 

## The excel report

>These notes more apply for code that will go in the teacherHelper module, but
>that is yet unfinished so here goes:

**Sheet 1**

- Columns:
    - Student Name
    - 

- Rows:
    - Grouped by "dynamic group" made by script.
