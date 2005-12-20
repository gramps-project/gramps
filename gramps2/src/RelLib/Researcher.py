class Researcher:
    """Contains the information about the owner of the database"""
    
    def __init__(self):
        """Initializes the Researcher object"""
        self.name = ""
        self.addr = ""
        self.city = ""
        self.state = ""
        self.country = ""
        self.postal = ""
        self.phone = ""
        self.email = ""

    def get_name(self):
        """returns the database owner's name"""
        return self.name

    def get_address(self):
        """returns the database owner's address"""
        return self.addr

    def get_city(self):
        """returns the database owner's city"""
        return self.city

    def get_state(self):
        """returns the database owner's state"""
        return self.state

    def get_country(self):
        """returns the database owner's country"""
        return self.country

    def get_postal_code(self):
        """returns the database owner's postal code"""
        return self.postal

    def get_phone(self):
        """returns the database owner's phone number"""
        return self.phone

    def get_email(self):
        """returns the database owner's email"""
        return self.email

    def set(self,name,addr,city,state,country,postal,phone,email):
        """sets the information about the database owner"""
        if name:
            self.name = name.strip()
        if addr:
            self.addr = addr.strip()
        if city:
            self.city = city.strip()
        if state:
            self.state = state.strip()
        if country:
            self.country = country.strip()
        if postal:
            self.postal = postal.strip()
        if phone:
            self.phone = phone.strip()
        if email:
            self.email = email.strip()

