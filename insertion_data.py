from App.Database.database import SessionLocal
from App.Utils.middleware import get_password_hash
from fastapi import Depends
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Menu.menu_model import Category_Model,Topping_Model,Size_Model,Pizza_Model
from App.DataModels.Order.order_model import Order_Model
from App.DataModels.Reviews.reviews_model import Review_Model
from App.DataModels.Payment.payment_model import Payment_Model
from App.DataModels.Notifications.notification_model import Notification_Model
from App.DataModels.Delivery.delivery_model import Delivery_Model
from App.Utils.constant import PizzaCategoryEnum,PizzaToppingEnum,PizzaSizeEnum
from App.DataModels.Cart.cart_model import Cart_Model
#1.=============Inserting Data in user Table==================
def insert_users():
    try:
        db=SessionLocal()
        hashed_password = get_password_hash("Ehti@123")
        users_list = []
        names = [
            "Ehtisham","Ahmed Ali", "Fatima Khan", "Zubair Sheikh", "Sana Malik", "Usman Ghani",
            "Ayesha Siddiqa", "Hamza Yusuf", "Bilal Ahmed", "Zainab Bibi", "Omer Farooq",
            "Maryam Nawaz", "Mustafa Kamal", "Hina Rabbani", "Asad Umar", "Faisal Javed",
            "Khadija Tul", "Imran Khan", "Babar Azam", "Rizwan Ahmed", "Shaheen Afridi"
        ]
        for i in range(21):
            clean_name = names[i].replace(" ", "").lower()
            new_user=User(
                full_name=names[i],
                email=f"{clean_name}exp@gmail.com",
                phone_number=f"0300{1000000 + i}",
                password=hashed_password,
                role="customer",
                is_active=False
            )
            users_list.append(new_user)
        db.add_all(users_list)
        db.commit()
        print("Message : Successfully Inserted the Data of All Users !")
    except Exception as e:
        db.rollback() 
        print(f"❌ DataBase Error: {e}")
    
    finally:
        db.close() 

#2.============= Database Seeding: Inserting Categories ==================
def insert_categories():
    db = None
    try:
        db = SessionLocal()
        
        # Mapping Enum to its Description
        # Hum direct Enum member pass karenge, values_callable use khud handle karega
        categories_to_insert = [
            (PizzaCategoryEnum.SIGNATURE, "Our timeless recipes featuring traditional flavors and high-quality ingredients."),
            (PizzaCategoryEnum.MEAT_FEAST, "A protein-packed delight loaded with premium pepperoni, succulent beef, and smoky chicken."),
            (PizzaCategoryEnum.GARDEN_FRESH, "A vibrant selection of garden-fresh vegetables and aromatic herbs."),
            (PizzaCategoryEnum.CHEESY, "The ultimate treat for cheese lovers, featuring a rich blend of melted cheeses."),
            (PizzaCategoryEnum.SPICY, "Turn up the heat with our selection of spicy jalapeños and zesty sauces."),
            (PizzaCategoryEnum.FUSION, "An adventurous mix of unique global flavors and gourmet toppings.")
        ]

        for cat_enum, cat_desc in categories_to_insert:
            # Check using the Enum member
            existing = db.query(Category_Model).filter(Category_Model.name == cat_enum).first()
            
            if not existing:
                new_category = Category_Model(
                    name = cat_enum, # SQLAlchemy will extract the .value because of our model fix
                    description = cat_desc
                )
                db.add(new_category)
                print(f"✅ Inserted: {cat_enum.value}")
            else:
                print(f"⚠️ Already exists: {cat_enum.value}")
        
        db.commit()
        print("🚀 Categories updated successfully!")
    
    except Exception as e:
        if db:
            db.rollback() 
        print(f"❌ DataBase Error: {e}")
    
    finally:
        if db:
            db.close()

#3.============= Database Seeding: Inserting Toppings ==================
def insert_toppings():
    db=None
    try:
        db=SessionLocal()
        toppings_to_insert=[topping.value for topping in PizzaToppingEnum]
        for topping_name in toppings_to_insert:
            # Check if the topping already exists in the database to prevent UNIQUE constraint violations
            existing = db.query(Topping_Model).filter(Topping_Model.name == topping_name).first()
            
            if not existing:
                # Create a new instance of the Topping_Model if it doesn't exist
                new_topping = Topping_Model(
                    name = topping_name,
                    extra_price = 150.0,
                    is_available=True  # Assigning a default price for all initial toppings
                )
                db.add(new_topping)
                print(f"✅ Inserted Topping: {topping_name}")
            else:
                # Inform if the topping is already present in the database
                print(f"⚠️ Topping already exists: {topping_name}")
        
        # Save all changes to the database
        db.commit()
        print("🚀 All toppings processed successfully!")
    
    except Exception as e:
        # Roll back the transaction if an error occurs to maintain data integrity
        if db:
            db.rollback()
        print(f"❌ DataBase Error: {e}")
    finally:
        # Close the session to free up database resources
        if db:
            db.close()

#4)============= Database Seeding: Inserting Pizza Sizes ==================
def insert_pizza_sizes():
    """
    Function to seed the database with pizza sizes and their price multipliers.
    It uses PizzaSizeEnum values to ensure consistency with the schema.
    """
    db = None
    try:
        # Initialize the database session
        db = SessionLocal()
        
        # Defining data with size names and their corresponding price multipliers
        # Multipliers: Small (1.0), Medium (1.5), Large (2.0), etc.
        sizes_data = [
            {"size": PizzaSizeEnum.SMALL, "multiplier": 1.0},
            {"size": PizzaSizeEnum.MEDIUM, "multiplier": 1.5},
            {"size": PizzaSizeEnum.LARGE, "multiplier": 2.0},
            {"size": PizzaSizeEnum.EXTRA_LARGE, "multiplier": 2.5}
        ]

        for item in sizes_data:
            # Check if the size already exists in the database to prevent UNIQUE constraint error
            existing = db.query(Size_Model).filter(Size_Model.size == item["size"]).first()
            
            if not existing:
                # Create a new Size_Model instance if the record is missing
                new_size = Size_Model(
                    size = item["size"], 
                    price_multiplier = item["multiplier"]
                )
                db.add(new_size)
                print(f"✅ Inserted Size: {item['size'].value} with Multiplier: {item['multiplier']}")
            else:
                # Skip insertion if the size is already present
                print(f"⚠️ Size already exists: {item['size'].value}")
        
        # Commit the transaction to save all records
        db.commit()
        print("🚀 Pizza sizes seeding completed successfully!")
    
    except Exception as e:
        # Rollback the transaction in case of any database or validation error
        if db:
            db.rollback() 
        print(f"❌ DataBase Error: {e}")
    
    finally:
        # Close the session to release database connection resources
        if db:
            db.close() 

# 5) ============= Database Seeding: Inserting 10 Pizzas ==================
def insert_pizzas():
    """
    Function to seed the database with an initial list of 10 pizzas.
    It dynamically fetches category IDs from the database to ensure 
    referential integrity.
    """
    db = None
    try:
        db = SessionLocal()

        # 1. Fetch Categories to link with Pizzas
        # We fetch the category objects to get their 'id'
        sig_cat = db.query(Category_Model).filter(Category_Model.name == "Signature & Classics").first()
        meat_cat = db.query(Category_Model).filter(Category_Model.name == "Meat Feast").first()
        veg_cat = db.query(Category_Model).filter(Category_Model.name == "Garden Fresh").first()
        spicy_cat = db.query(Category_Model).filter(Category_Model.name == "Hot & Spicy").first()

        # Fallback in case categories are missing
        if not all([sig_cat, meat_cat, veg_cat, spicy_cat]):
            print("❌ Error: Categories not found. Please run the category seeding script first.")
            return

        # 2. List of 10 Pizzas to insert
        pizzas_to_seed = [
            {"name": "Chicken Tikka", "price": 1200.0, "cat": sig_cat.id, "desc": "Traditional tikka chunks with onions."},
            {"name": "Pepperoni Passion", "price": 1450.0, "cat": meat_cat.id, "desc": "Extra pepperoni with double mozzarella."},
            {"name": "Veggie Supreme", "price": 1100.0, "cat": veg_cat.id, "desc": "Bell peppers, olives, mushrooms, and onions."},
            {"name": "Fiery Jalapeno", "price": 1300.0, "cat": spicy_cat.id, "desc": "Spicy chicken with a heavy dose of jalapenos."},
            {"name": "Beef Delight", "price": 1600.0, "cat": meat_cat.id, "desc": "Premium ground beef with smoky BBQ sauce."},
            {"name": "Fajita Sensation", "price": 1250.0, "cat": sig_cat.id, "desc": "Marinated fajita chicken and green peppers."},
            {"name": "Mushroom Magic", "price": 1150.0, "cat": veg_cat.id, "desc": "Freshly sliced mushrooms and creamy white sauce."},
            {"name": "Peri Peri Blast", "price": 1400.0, "cat": spicy_cat.id, "desc": "Hot peri-peri chicken with spicy red chilies."},
            {"name": "Cheese Lover", "price": 1000.0, "cat": sig_cat.id, "desc": "A rich blend of cheddar, mozzarella, and parmesan."},
            {"name": "BBQ Chicken", "price": 1350.0, "cat": meat_cat.id, "desc": "Grilled chicken tossed in sweet and tangy BBQ sauce."}
        ]

        for p_data in pizzas_to_seed:
            # Check if pizza already exists by name
            existing = db.query(Pizza_Model).filter(Pizza_Model.name == p_data["name"]).first()
            
            if not existing:
                # Creating new Pizza_Model instance
                new_pizza = Pizza_Model(
                    name = p_data["name"],
                    description = p_data["desc"],
                    base_price = p_data["price"],
                    category_id = p_data["cat"],
                    image_url = f"uploads/pizzas/{p_data['name'].lower().replace(' ', '_')}.jpg",
                    is_available = True
                )
                db.add(new_pizza)
                print(f"✅ Inserted: {p_data['name']}")
            else:
                print(f"⚠️ Already exists: {p_data['name']}")

        # 3. Commit the changes
        db.commit()
        print("🚀 Successfully seeded 10 pizzas into the database!")

    except Exception as e:
        if db:
            db.rollback()
        print(f"❌ DataBase Error: {e}")
    finally:
        if db:
            db.close()



if __name__=="__main__":
    # insert_toppings()
    # insert_pizza_sizes()
    insert_pizzas()
    # insert_users()
    # insert_categories()
    



