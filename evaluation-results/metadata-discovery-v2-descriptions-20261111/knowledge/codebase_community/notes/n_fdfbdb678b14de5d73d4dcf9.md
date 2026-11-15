# postLinks.PostId

Type: column
Table: postLinks
Scope: PostId
Summary: Nullable integer referencing the post at the PostId endpoint of a post-link record.
Keywords: postlinks, postid, linked post, foreign key
Status: provisional
Sources: schema:postLinks DDL (nullable PostId foreign key to posts.Id); description:postLinks.csv:3 (PostId is the post id)

## Business Meaning
Identifier of the post at the PostId endpoint in a post-link record.
## Business Usage
Joins to posts.Id to identify the source-side post in the stored link; the directionality's business semantics are Unknown / Not verified.
## Value Meaning
Nullable INTEGER; schema declares a foreign key to posts.Id. No special code interpretation applies.
## Calculation Meaning
N/A; source/pass-through field.
