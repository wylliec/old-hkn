ALTER TABLE "review_problem" DROP COLUMN "submitter";
ALTER TABLE "review_problem" ADD COLUMN "submitted" timestamp with time zone NOT NULL;
ALTER TABLE "review_problem" ADD COLUMN "submitter_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
