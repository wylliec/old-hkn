from django.core.management.base import NoArgsCommand                                                            
class Command(NoArgsCommand):
    help = """
    Deletes orphaned request objects (whose related objects don't exist).
    """

    def handle_noargs(self, **options):
        from request.models import Request
        for orphan in filter(lambda r: r.confirm_object is None, Request.objects.all()):
            print "DELETING ORPHAN: %s" % orphan.description
            orphan.delete()
        print "Finished deleting orphans"

