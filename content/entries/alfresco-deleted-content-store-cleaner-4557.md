---

title: "Alfresco Deleted Content Store Cleaner"
description: "This add-on provide a job to remove abandoned files in Deleted Content Store. From Alfresco 5.2 (201707 GA) a **Trashcan Cleaner** job is provided out of the box, although is disabled by default. This job removes documents from trash can periodically. Once a content has been deleted from trashcan, `ContentStoreCleaner` job moves it to Deleted Content Store and change node state to `deleted` in database 14 days after. `NodeServiceCleanup` job remove the node from database 30 days after, but in the end the file is still living in Deleted Content Store. This addon will purge from Deleted Content Store (usually at `${alfresco}/alf_data/contentstore.deleted`) these abandoned files."
screenshots: []
compatibility: ["5.2.x", "5.2.x"]
license: "LGPL-3.0-or-later"
keywords: ["alfresco", "addon", "plugin", "community", "keensoft"]
download_url: "https://github.com/keensoft/alfresco-deleted-content-store-cleaner"
vendor: "Angel Borroy ‌"
about: ""
about_url: "https://github.com/keensoft/alfresco-deleted-content-store-cleaner"
draft: true

---
