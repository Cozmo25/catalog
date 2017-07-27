from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Store, Base, Product, User

engine = create_engine('sqlite:///products.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Ollie", email="olliegraham@gmail.com",
             picture='https://media.licdn.com/mpr/mpr/\
             shrinknp_400_400/AAEAAQAAAAAAAAe9AAAAJDY4Yjg\
             4ZjYwLTkxZTEtNDQzMi1hOWFiLTg2Y2I0YzlhODVlOQ.jpg')
session.add(User1)
session.commit()

# Evo Gear Store
store1 = Store(user_id=1, name="Evo Gear")

session.add(store1)
session.commit()

product1 = Product(user_id=1, name="Slayer",
                   description="Slay the mountain with the Slayer!",
                   price="$750", size="158 - 170cm", category="boards", store=store1)

session.add(product1)
session.commit()

product2 = Product(user_id=1, name="Genesis",
                   description="Burton's Genesis the lightest bindings you can buy",
                   price="$250", size="S - L", category="bindings", store=store1)

session.add(product2)
session.commit()


product3 = Product(user_id=1, name="Ion", description="Stiff freeride boot",
                     price="$199", size="6 - 12", category="boots", store=store1)

session.add(product3)
session.commit()


# Backcountry.com Store
store2 = Store(user_id=1, name="Backcountry.com")

session.add(store2)
session.commit()

product1 = Product(user_id=1, name="Union Travis Rice",
                   description="Nail the Backcountry\
                    with these unbreakable bindings",
                   price="$399", size="S - L", category="bindings", store=store2)

session.add(product1)
session.commit()


product2 = Product(user_id=1, name="Skate Banana",
                   description="Jib till your legs fall off!",
                   price="$399", size="154cm", category="boards", store=store2)

session.add(product2)
session.commit()


product3 = Product(user_id=1, name="Board Wax", description="Get those high speed laps in with this baord wax for all conditions",
                     price="$13.95", size="One size", category="accessory", store=store2)

session.add(product3)
session.commit()

# The-House Store
store3 = Store(user_id=1, name="The House")

session.add(store3)
session.commit()


product1 = Product(user_id=1, name="Flagship",
                   description="Jones Snowbaords Flagship model",
                   price="$650", size="158cm - 171cm", category="boards", store=store3)

session.add(product1)
session.commit()


product2 = Product(user_id=1, name="Ruler", description="Mid flex park boot",
                     price="$89", size="6 - 12", category="boots", store=store3)

session.add(product2)
session.commit()


product3 = Product(user_id=1, name="Down Jacket", description="Wrap up warm on those really cold days",
                     price="$199", size="S - XL", category="outerwear", store=store3)

session.add(product3)
session.commit()


# Surfdome
store4 = Store(user_id=1, name="Surfdome")

session.add(store4)
session.commit()


product2 = Product(user_id=1, name="Volcom Guide Jacket", description="Goretex Jacket - stay dry all day",
                     price="$399", size="S - XL", category="outerwear", store=store4)

session.add(product2)
session.commit()

product3 = Product(user_id=1, name="Volcom Guide Pants",
                   description="Goretex Pants are lightweight and breathable to keep you warm & dry",
                   price="$250", size="S - XL", category="outerwear", store=store4)

session.add(product3)
session.commit()


# Blue Tomato
store5 = Store(user_id=1, name="Blue Tomato")

session.add(store5)
session.commit()


product1 = Product(user_id=1, name="Board Lock", description="Make sure someone doesn't run off with your ride with this board lock",
                     price="$4.95", size="One Size", category="accessory", store=store5)

session.add(product1)
session.commit()

product2 = Product(user_id=1, name="Stomp Pad", description="No more slipping on your butt in the lift line with this stomp pad stuck on your board",
                     price="$6.95", size="One Size", category="accessory", store=store5)

session.add(product3)
session.commit()


print "added snowboard products!"
