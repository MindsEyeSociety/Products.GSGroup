# coding=utf-8
import sqlalchemy as sa

class GroupQuery(object):

    def __init__(self, context, da):
        self.context = context
        self.postTable = da.createTable('post')
        
    def authors_posts_in_group(self, siteId, groupId):
        pt = self.postTable
        cols = [pt.c.user_id.distinct(),
                sa.func.count(pt.c.user_id).label('num_posts')]
        statement = sa.select(cols)
        statement.append_whereclause(pt.c.site_id==siteId)
        statement.append_whereclause(pt.c.group_id==groupId)
        statement.group_by(pt.c.user_id)

        r = statement.execute()
        retval = []
        if r.rowcount:
            for row in r:
                retval.append({'user_id': row['user_id'], 
                               'num_posts': row['num_posts']})
        return retval


    