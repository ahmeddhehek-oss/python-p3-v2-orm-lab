from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    @property
    def year(self):
        return self._year
    @year.setter
    def year(self, value):
          if type(value) is not int:
                raise ValueError("Year must be an integer")
          if value < 2000:
                raise ValueError("Year must be 2000 or later")
          self._year = value
    @property
    def summary(self):
        return self._summary
    @summary.setter
    def summary(self, value):
        if type(value) is not str:
            raise ValueError("Summary must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Summary cannot be empty")
        self._summary = value
    @property
    def employee_id(self):
        return self._employee_id
    @employee_id.setter
    def employee_id(self, value):
        from employee import Employee
        if type(value) is not int:
            raise ValueError("Employee ID must be an integer")
        employee = Employee.find_by_id(value)
        if not employee:
            raise ValueError("Employee ID must reference an existing Employee")
        self._employee_id = value

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            self.update()
            return self
               
        

    @classmethod
    def create(cls, year, summary, employee_id):
        Review = cls(year, summary, employee_id)
        Review.save()
        return Review
    
   
    @classmethod
    def instance_from_db(cls, row):
        Review_id = row[0]
        if Review_id in cls.all:
            instance = cls.all[Review_id]
            instance.year = row[1]
            instance.summary = row[2]
            instance.employee_id = row[3]
            return instance
        instance = cls(row[1], row[2], row[3], id=row[0])
        cls.all[Review_id] = instance
        return instance
        
   

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?" 
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None
        

    def update(self):
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()
      

    def delete(self):
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in Review.all:
            del Review.all[self.id]
            self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

