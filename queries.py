# Queries related to groups
import sqlalchemy as sa

class GroupQuery(object):

    def __init__(self, context, da):
        self.context = context

        self.postTable = da.createMapper('post')[1] 
        
    def authors_posts_in_group(self, siteId, groupId):
        pt = self.postTable
        statement = sa.select([pt.c.user_id.distinct().label('author'), sa.func.count(pt.c.user_id).label('num_posts')])
        statement.append_whereclause(pt.c.site_id==siteId)
        statement.append_whereclause(pt.c.group_id==groupId)
        statement.group_by([pt.c.user_id])

        r = statement.execute()
        retval = []
        if r.rowcount:
            for row in r:
                retval.append = {'author': row['author'], 'num_posts': row['num_posts']}
        return retval

