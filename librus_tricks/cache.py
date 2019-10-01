from datetime import datetime

from sqlalchemy import create_engine, String, JSON, Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


class CacheBase:
    def add_object(self, uid, cls, resource):
        pass

    def get_object(self, uid, cls):
        raise NotImplementedError('get_object require implementation')

    def del_object(self, uid):
        raise NotImplementedError('del_object require implementation')

    def add_query(self, uri, response, user_id):
        pass

    def get_query(self, uri, user_id):
        raise NotImplementedError('get_query require implementation')

    def del_query(self, uri, user_id):
        raise NotImplementedError('del_query require implementation')


class DumbCache(CacheBase):
    def get_object(self, uid, cls):
        return

    def get_query(self, uri, user_id):
        return


class AlchemyCache(CacheBase):
    Base = declarative_base()

    def __init__(self, engine_uri='sqlite:///:memory:'):
        engine = create_engine(engine_uri, connect_args={'check_same_thread': False}, poolclass=StaticPool)

        Session = sessionmaker(bind=engine)
        Session.configure(bind=engine)
        self.session = Session()
        self.Base.metadata.create_all(engine)
        self.syn_session = None

    class APIQueryCache(Base):
        __tablename__ = 'uri_cache'

        pk = Column(Integer(), primary_key=True)
        uri = Column(String(length=512))
        owner = Column(String(length=16))
        response = Column(JSON())
        last_load = Column(DateTime())

    class ObjectLoadCache(Base):
        __tablename__ = 'object_cache'

        uid = Column(Integer(), primary_key=True)
        name = Column(String(length=64))
        resource = Column(JSON())
        last_load = Column(DateTime())

    def add_object(self, uid, cls, resource):
        self.session.add(
            self.ObjectLoadCache(uid=uid, name=cls.__name__, resource=resource, last_load=datetime.now())
        )
        self.session.commit()

    def get_object(self, uid, cls):
        """

        :rtype: AlchemyCache.ObjectLoadCache
        """
        response = self.session.query(self.ObjectLoadCache).filter_by(uid=uid, name=cls.__name__).first()
        if response is None:
            return None
        return cls.assembly(response.resource, self.syn_session)

    def add_query(self, uri, response, user_id):
        self.session.add(
            self.APIQueryCache(uri=uri, response=response, last_load=datetime.now(), owner=user_id)
        )
        self.session.commit()

    def get_query(self, uri, user_id):
        """

        :rtype: AlchemyCache.APIQueryCache
        """
        return self.session.query(self.APIQueryCache).filter_by(uri=uri, owner=user_id).first()

    def del_query(self, uri, user_id):
        self.session.query(self.APIQueryCache).filter_by(uri=uri, owner=user_id).delete()
        self.session.commit()

    def del_object(self, uid):
        self.session.query(self.ObjectLoadCache).filter_by(uid=uid).delete()
        self.session.commit()
