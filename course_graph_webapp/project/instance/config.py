SECRET_KEY = 'p9Bv<3Eid9%$i01'
# SQLALCHEMY_DATABASE_URI = 'mysql://root:wangluyao0323@localhost/WebApp'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='wangluyao0323', server='localhost', database='WebApp')