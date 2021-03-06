from camelot.view.art import Icon
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section

class MyApplicationAdmin(ApplicationAdmin):

    name = 'Camelot Video Store'

    def get_sections(self):
        from camelot.model.memento import Memento
        from camelot.model.authentication import Person, Organization
        from camelot.model.i18n import Translation
        from model import Movie, Tag, VisitorReport
        return [Section('movies',
                        Icon('tango/22x22/mimetypes/x-office-presentation.png'),
                        items = [Movie, Tag, VisitorReport]),
                Section('relation',
                        Icon('tango/22x22/apps/system-users.png'),
                        items = [Person, Organization]),
                Section('configuration',
                        Icon('tango/22x22/categories/preferences-system.png'),
                        items = [Memento, Translation])
                ]
