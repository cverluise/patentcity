# DEDUPLICATION

## Problem

In some formats (e.g. uspatent01), patentees are reported twice on the same document. This can be detrimental to metrics such as the average number of inventors/assignees per patent, etc. We would like to flag duplicates to avoid results contamination.

## Approach

For each patent of affected formats, we look at the pairwise relative levenshtein distance of all detected patentee names. Then we look for the threshold maximizing accuracy (based on a manually labelled gold set).

!!! definition
    We call relative levenshtein distance the levenshtein distance between 2 strings (lower caps) divided by the average character lengths of the two strings

## Results

### `uspatent01`

!!! done
    - Best threshold: 0.43
    - Accuracy: 0.974
