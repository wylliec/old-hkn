CREATE TABLE "info_extendedinfo_current_courses" (
    "id" serial NOT NULL PRIMARY KEY,
    "extendedinfo_id" integer NOT NULL REFERENCES "info_extendedinfo" ("person_id") DEFERRABLE INITIALLY DEFERRED,
    "course_id" integer NOT NULL REFERENCES "course_course" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("extendedinfo_id", "course_id")
);

