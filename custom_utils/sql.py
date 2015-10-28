import sqlalchemy
from sqlalchemy import Column, ForeignKey, UniqueConstraint, PrimaryKeyConstraint, and_, or_
from sqlalchemy import create_engine, update, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


class Sql:

    def __init__(self, db_file, script_db_version):

        engine = create_engine('sqlite:///' + db_file)

        self.script_db_version = str(script_db_version)
        # Create if it does not exist
        Base.metadata.create_all(engine)

        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self._session = DBSession()

    def get_session(self):
        return self._session

    def get_progress(self):
        """
        :return: int of progress
        """
        progress = self._session.query(Setting.value).filter_by(field='progress').first()[0]
        return int(progress)

    def update_progress(self, new_progress):
        """
        update progress value in database
        """
        self._session.query(Setting).filter(Setting.field == 'progress').update({Setting.value: new_progress})
        self._session.commit()

    def set_up_db(self):
        """
        :return: Tuple (<bool of versions match>, <current db version>)
        """
        # Check database version
        try:
            curr_db_version = self._session.query(Setting.value).filter_by(field='db_version').first()[0]
        except TypeError:
            # If we get a None type, then settings db is empty, so create the basics
            curr_db_version = self.script_db_version
            setting_db_version = Setting(field='db_version', value=self.script_db_version)
            # Initial progress value needs to be -1 so we can start on index 0
            setting_progress = Setting(field='progress', value=-1)
            self._session.add(setting_db_version)
            self._session.add(setting_progress)
            self._session.commit()

        is_same_version = curr_db_version == self.script_db_version
        return (is_same_version, curr_db_version)


###
# Database setup
###
Base = declarative_base()


class Setting(Base):
    __tablename__ = 'settings'
    field = Column(String(50), primary_key=True)
    value = Column(String(50), nullable=False)
