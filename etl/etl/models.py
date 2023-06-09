from sqlalchemy import Integer, Float, Column, Index, create_engine, func
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from io import StringIO
import csv
import logging

logger = logging.getLogger(__name__)
engine = None
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Impression(Base):
    __tablename__ = "impression"

    impression_id = Column(Integer, nullable=False, primary_key=True)
    quarter = Column(Integer, nullable=False)
    campaign_id = Column(Integer, nullable=False)
    banner_id = Column(Integer, nullable=False)
    total_clicks = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    __table_args__ = (Index('impression_index', "quarter", "campaign_id", "banner_id"),)

    def __repr__(self) -> str:
        return f"Impression(Impression_id={self.impression_id!r}, quarter={self.quarter!r}, " \
               f"campaign_id={self.campaign_id!r}, banner_id={self.banner_id!r}, total_clicks={self.total_clicks!r}, " \
               f"total_revenue={self.total_revenue!r})"


def import_impressions(logfile, data, quarter):
    with open(logfile, 'w+') as f:
        f.truncate(0)
        total_added = 0
        cur_line = 0
        with Session() as session:
            entities = []
            csvreader = csv.reader(StringIO(data), delimiter=',')
            next(csvreader)
            for row in csvreader:
                cur_line += 1
                if cur_line % 10000 == 0:
                    logger.info("{} impression records processed by now.".format(cur_line))
                banner_id = int(row[0])
                campaign_id = int(row[1])

                existing_entity = session.query(Impression).filter_by(quarter=quarter, campaign_id=campaign_id,
                                                                      banner_id=banner_id).first()
                if existing_entity:
                    f.write("Row number {} already exists in the database!\n".format(cur_line))
                else:
                    total_added += 1
                    entities.append(Impression(quarter=quarter, campaign_id=campaign_id, banner_id=banner_id))

            if total_added > 0:
                revision = session.query(Revision).first()
                revision.revision += 1
                entities.append(revision)

            session.bulk_save_objects(entities)
            session.commit()
        result = "{0} from {1} impression rows successfully added to database.".format(total_added, cur_line)
        f.write(result + "\nThe import process has finished.\n")
        logger.info(result)


class Click(Base):
    __tablename__ = "click"

    click_id = Column(Integer, nullable=False, primary_key=True)
    campaign_id = Column(Integer, nullable=False)
    banner_id = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"Click(click_id={self.click_id!r}, campaign_id={self.campaign_id!r}, banner_id={self.banner_id!r}, " \
               f"quarter={self.quarter!r})"


def import_clicks(logfile, data, quarter):
    new_clicks = []
    total_added = 0
    with open(logfile, 'w+') as f:
        f.truncate(0)
        cur_line = 0
        with Session() as session:
            entities = []
            csvreader = csv.reader(StringIO(data), delimiter=',')
            next(csvreader)
            for row in csvreader:
                cur_line += 1
                if cur_line % 10000 == 0:
                    logger.info("{} click records processed by now.".format(cur_line))
                click_id = int(row[0])
                banner_id = int(row[1])
                campaign_id = int(row[2])

                existing_entity = session.query(Click).get(click_id)
                if existing_entity:
                    f.write("Row number {} already exists in the database!\n".format(cur_line))
                else:
                    total_added += 1
                    new_clicks.append(click_id)
                    entities.append(Click(quarter=quarter, click_id=click_id, banner_id=banner_id,
                                          campaign_id=campaign_id))
                    existing_impressions = session.query(Impression).filter_by(quarter=quarter, campaign_id=campaign_id,
                                                                               banner_id=banner_id).first()
                    if existing_impressions is None:
                        entities.append(Impression(quarter=quarter, campaign_id=campaign_id, banner_id=banner_id))
            session.bulk_save_objects(entities)
            session.commit()
        result = "{0} from {1} click rows successfully added to database.".format(total_added, cur_line)
        f.write(result + "\nThe import process has finished.\n")
        logger.info(result)
    if total_added > 0:
        update_with_clicks(new_clicks)


def update_with_clicks(clicks):
    with Session() as session:
        data = {}
        for click_id in clicks:
            click = session.query(Click).get(click_id)
            impression = session.query(Impression).filter_by(quarter=click.quarter, campaign_id=click.campaign_id,
                                                             banner_id=click.banner_id).first()
            if impression.impression_id in data:
                data[impression.impression_id] += 1
            else:
                data[impression.impression_id] = 1

        entities = []
        for k, v in data.items():
            impression = session.query(Impression).get(k)
            impression.total_clicks += v
            entities.append(impression)

        revision = session.query(Revision).first()
        revision.revision += 1
        entities.append(revision)

        session.bulk_save_objects(entities)
        session.commit()


class Conversion(Base):
    __tablename__ = "conversion"

    conversion_id = Column(Integer, nullable=False, primary_key=True)
    click_id = Column(Integer, nullable=False)
    revenue = Column(Float, default=0.0)
    quarter = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"Conversion(conversion_id={self.conversion_id!r}, click_id={self.click_id!r}, " \
               f"revenue={self.revenue!r}, quarter={self.quarter!r})"


def import_conversions(logfile, data, quarter):
    new_conversions = {}
    total_added = 0
    with open(logfile, 'w+') as f:
        f.truncate(0)
        cur_line = 0
        with Session() as session:
            entities = []
            csvreader = csv.reader(StringIO(data), delimiter=',')
            next(csvreader)
            for row in csvreader:
                cur_line += 1
                if cur_line % 10000 == 0:
                    logger.info("{} conversion records processed by now.".format(cur_line))
                conversion_id = int(row[0])
                click_id = int(row[1])
                revenue = float(row[2])

                existing_entity = session.query(Conversion).get(conversion_id)
                if existing_entity:
                    f.write("Row number {} already exists in the database!\n".format(cur_line))
                else:
                    total_added += 1
                    entities.append(Conversion(quarter=quarter, click_id=click_id, conversion_id=conversion_id,
                                               revenue=revenue))
                    if click_id in new_conversions:
                        new_conversions[click_id] += revenue
                    else:
                        new_conversions[click_id] = revenue
            session.bulk_save_objects(entities)
            session.commit()
        result = "{0} from {1} conversion rows successfully added to database.".format(total_added, cur_line)
        f.write(result + "\nThe import process has finished.\n")
        logger.info(result)
    if total_added > 0:
        update_with_conversions(new_conversions)


def update_with_conversions(conversions):
    with Session() as session:
        data = {}
        for k, v in conversions.items():
            click = session.query(Click).get(k)
            # TODO: handling conversions that their click doesn't exist
            if click is None:
                continue
            impression = session.query(Impression).filter_by(quarter=click.quarter, campaign_id=click.campaign_id,
                                                             banner_id=click.banner_id).first()
            if impression.impression_id in data:
                data[impression.impression_id] += v
            else:
                data[impression.impression_id] = v

        entities = []
        for k, v in data.items():
            impression = session.query(Impression).get(k)
            impression.total_revenue += v
            entities.append(impression)

        revision = session.query(Revision).first()
        revision.revision += 1
        entities.append(revision)

        session.bulk_save_objects(entities)
        session.commit()


class Revision(Base):
    __tablename__ = "revision"

    id = Column(Integer, nullable=False, primary_key=True)
    revision = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"Revision(id={self.id!r}, revision={self.revision!r})"


def get_data_revision():
    with Session() as session:
        revision = session.query(Revision).first()
        return revision.revision


def get_tops_by_revenue(quarter, campaign_id):
    with Session() as session:
        tops = session.query(Impression.banner_id, Impression.total_revenue)\
            .filter_by(quarter=quarter, campaign_id=campaign_id)\
            .order_by(Impression.total_revenue.desc()).limit(10).all()

        tops_with_conversion = []
        for row in tops:
            if float(row[1]) > 0.0:
                tops_with_conversion.append(row[0])
        return tops_with_conversion


def get_tops_by_clicks(quarter, campaign_id):
    with Session() as session:
        tops = session.query(Impression.banner_id, Impression.total_clicks)\
            .filter_by(quarter=quarter, campaign_id=campaign_id)\
            .order_by(Impression.total_clicks.desc()).limit(10).all()

        tops_with_click = []
        for row in tops:
            if int(row[1]) > 0:
                tops_with_click.append(row[0])
        return tops_with_click


def get_tops_by_random(quarter, campaign_id):
    with Session() as session:
        tops = session.query(Impression.banner_id)\
            .filter_by(quarter=quarter, campaign_id=campaign_id)\
            .order_by(func.random()).limit(5).all()
        return [row[0] for row in tops]


def create_db_connection(configs):
    global engine
    engine = create_engine("mysql+pymysql://{0}:{1}@{2}/{3}?charset=utf8mb4"
                           .format(configs.MYSQL_USER,
                                   configs.MYSQL_PASS,
                                   configs.MYSQL_ADDR,
                                   configs.MYSQL_DB),
                           echo=False)
    global Session
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine, checkfirst=True)

    with Session() as session:
        revision = session.query(Revision).first()
        if revision is None:
            revision = Revision(revision=0)
            session.add(revision)
            session.commit()
