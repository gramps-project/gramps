from _FilterSpecBase import FilterSpecBase

class PersonFilterSpec(FilterSpecBase):

    BEFORE = 1
    AFTER = 2
    
    def __init__(self):
        FilterSpecBase.__init__(self)
        
        self._name = None
        self._gender = None
        self._birth_year = None
        self._birth_criteria = self.__class__.BEFORE
        self._death_year = None
        self._death_criteria = self.__class__.BEFORE

    def set_name(self,name):
        self._name = name

    def get_name(self):
        return self._name

    def include_name(self):
        return self._name is not None

    def set_gender(self,gender):
        self._gender = gender

    def get_gender(self):
        return self._gender

    def include_gender(self):
        return self._gender is not None

    def set_birth_year(self,year):
        self._birth_year = str(year)

    def get_birth_year(self):
        return self._birth_year

    def include_birth(self):
        return self._birth_year is not None

    def set_birth_criteria(self,birth_criteria):
        self._birth_criteria = birth_criteria

    def get_birth_criteria(self):
        return self._birth_criteria

    def set_death_year(self,year):
        self._death_year = str(year)

    def get_death_year(self):
        return self._death_year

    def include_death(self):
        return self._death_year is not None

    def set_death_criteria(self,death_criteria):
        self._death_criteria = death_criteria

    def get_death_criteria(self):
        return self._death_criteria

