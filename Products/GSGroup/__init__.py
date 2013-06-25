# This space intentionally left blank
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class

module_security = ModuleSecurityInfo('Products.GSGroup')
groupInfo_security = ModuleSecurityInfo('Products.GSGroup.groupInfo')
from groupInfo import GSGroupInfoFactory, GSGroupInfo
allow_class(GSGroupInfoFactory)
allow_class(GSGroupInfo)
