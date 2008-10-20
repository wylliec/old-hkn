DROP TABLE "review_problem";
BEGIN;
CREATE TABLE "review_problem" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(150) NOT NULL,
    "description" text NOT NULL,
    "tags" varchar(255) NOT NULL,
    "difficulty" double precision NULL,
    "question" varchar(100) NULL,
    "answer" varchar(100) NULL,
    "submitted" timestamp with time zone NOT NULL,
    "submitter_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "num_ratings" integer NOT NULL
)
;
COMMIT;
