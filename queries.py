# coding=utf-8
import sqlalchemy as sa

class GroupQuery(object):

    def __init__(self, context, da):
        self.context = context
        self.postTable = da.createTable('post')
        self.userInvitationTable = da.createTable('user_group_member_invitation')
        
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

    def get_current_invitations_for_group(self, siteId, groupId):
        assert siteId
        assert groupId
        uit = self.userInvitationTable
        cols = [uit.c.site_id, uit.c.group_id, uit.c.user_id,
                uit.c.inviting_user_id, uit.c.invitation_date, 
                uit.c.response_date]
        s = sa.select(cols)
        s.append_whereclause(uit.c.site_id  == siteId)
        s.append_whereclause(uit.c.group_id  == groupId)
        s.append_whereclause(uit.c.response_date == None)
        s.order_by(sa.desc('invitation_date'))
        
        r = s.execute()
        retval = []
        if r.rowcount:
            retval = [{
              'site_id':          x['site_id'],
              'group_id':         x['group_id'],
              'user_id':          x['user_id'],
              'inviting_user_id': x['inviting_user_id'],
              'invitation_date':  x['invitation_date']} for x in r]

        assert type(retval) == list
        return retval
    
    