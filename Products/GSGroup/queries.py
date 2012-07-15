# coding=utf-8
from gs.database import getTable, getSession
import sqlalchemy as sa

class GroupQuery(object):
    def __init__(self, context):
        self.context = context
        self.postTable = getTable('post')
        
    def authors_posts_in_group(self, siteId, groupId):
        pt = self.postTable
        cols = [pt.c.user_id.distinct(),
                sa.func.count(pt.c.user_id).label('num_posts')]
        statement = sa.select(cols, group_by=pt.c.user_id)
        statement.append_whereclause(pt.c.site_id == siteId)
        statement.append_whereclause(pt.c.group_id == groupId)
        
        session = getSession()
        r = session.execute(statement)
        retval = []
        if r.rowcount:
            for row in r:
                retval.append({'user_id': row['user_id'],
                               'num_posts': row['num_posts']})
        return retval

