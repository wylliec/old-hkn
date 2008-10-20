ALTER TABLE "review_problem" ADD COLUMN "submitted" datetime NOT NULL;
ALTER TABLE "review_problem" ADD COLUMN "submitter" integer NULL REFERENCES "auth_user" ("id");
