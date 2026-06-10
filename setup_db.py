"""Create Chinook database for QueryMind."""

import sqlite3
import os

def create_chinook_db():
    """Create the Chinook database with sample music store data."""
    db_path = "database/chinook.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artists (
        ArtistId INTEGER PRIMARY KEY,
        Name TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS albums (
        AlbumId INTEGER PRIMARY KEY,
        Title TEXT NOT NULL,
        ArtistId INTEGER NOT NULL,
        FOREIGN KEY (ArtistId) REFERENCES artists(ArtistId)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS genres (
        GenreId INTEGER PRIMARY KEY,
        Name TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        TrackId INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        AlbumId INTEGER NOT NULL,
        MediaTypeId INTEGER,
        GenreId INTEGER,
        Composer TEXT,
        Milliseconds INTEGER,
        Bytes INTEGER,
        UnitPrice REAL,
        FOREIGN KEY (AlbumId) REFERENCES albums(AlbumId),
        FOREIGN KEY (GenreId) REFERENCES genres(GenreId)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        CustomerId INTEGER PRIMARY KEY,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        Company TEXT,
        Address TEXT,
        City TEXT,
        State TEXT,
        PostalCode TEXT,
        Country TEXT,
        Phone TEXT,
        Email TEXT,
        SupportRepId INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        EmployeeId INTEGER PRIMARY KEY,
        LastName TEXT NOT NULL,
        FirstName TEXT NOT NULL,
        Title TEXT,
        ReportsTo INTEGER,
        BirthDate TEXT,
        HireDate TEXT,
        Address TEXT,
        City TEXT,
        State TEXT,
        PostalCode TEXT,
        Country TEXT,
        Phone TEXT,
        Email TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        InvoiceId INTEGER PRIMARY KEY,
        CustomerId INTEGER NOT NULL,
        InvoiceDate TEXT,
        BillingAddress TEXT,
        BillingCity TEXT,
        BillingState TEXT,
        BillingPostalCode TEXT,
        BillingCountry TEXT,
        Total REAL,
        FOREIGN KEY (CustomerId) REFERENCES customers(CustomerId)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        InvoiceLineId INTEGER PRIMARY KEY,
        InvoiceId INTEGER NOT NULL,
        TrackId INTEGER NOT NULL,
        UnitPrice REAL,
        Quantity INTEGER,
        FOREIGN KEY (InvoiceId) REFERENCES invoices(InvoiceId),
        FOREIGN KEY (TrackId) REFERENCES tracks(TrackId)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists (
        PlaylistId INTEGER PRIMARY KEY,
        Name TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist_track (
        PlaylistId INTEGER NOT NULL,
        TrackId INTEGER NOT NULL,
        PRIMARY KEY (PlaylistId, TrackId),
        FOREIGN KEY (PlaylistId) REFERENCES playlists(PlaylistId),
        FOREIGN KEY (TrackId) REFERENCES tracks(TrackId)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS media_types (
        MediaTypeId INTEGER PRIMARY KEY,
        Name TEXT NOT NULL
    )
    """)
    
    # Insert sample data
    artists_data = [
        (1, "AC/DC"),
        (2, "Miles Davis"),
        (3, "The Beatles"),
        (4, "Pink Floyd"),
        (5, "Led Zeppelin"),
    ]
    cursor.executemany("INSERT INTO artists VALUES (?, ?)", artists_data)
    
    genres_data = [
        (1, "Rock"),
        (2, "Jazz"),
        (3, "Pop"),
        (4, "Classical"),
        (5, "Electronic"),
    ]
    cursor.executemany("INSERT INTO genres VALUES (?, ?)", genres_data)
    
    albums_data = [
        (1, "Let It Be", 3),
        (2, "The Wall", 4),
        (3, "Back in Black", 1),
        (4, "Dark Side of the Moon", 4),
        (5, "Led Zeppelin IV", 5),
    ]
    cursor.executemany("INSERT INTO albums VALUES (?, ?, ?)", albums_data)
    
    tracks_data = [
        (1, "Let It Be", 1, 1, 1, "McCartney", 243000, 1000000, 0.99),
        (2, "The Long and Winding Road", 1, 1, 1, "McCartney", 213000, 900000, 0.99),
        (3, "Comfortably Numb", 2, 1, 1, "Gilmour, Waters", 384000, 1500000, 0.99),
        (4, "Back in Black", 3, 1, 1, "Scott, Young", 255000, 1200000, 0.99),
        (5, "Money", 4, 1, 1, "Waters", 382000, 1400000, 0.99),
        (6, "Whole Lotta Love", 5, 1, 1, "Led Zeppelin", 345000, 1100000, 0.99),
        (7, "Jazz Standard 1", 1, 1, 2, "Davis", 300000, 950000, 0.99),
        (8, "Midnight in Blue", 2, 1, 2, "Davis", 320000, 1050000, 0.99),
        (9, "Pop Hit 1", 3, 1, 3, "Unknown", 200000, 800000, 0.99),
        (10, "Electronic Dreams", 4, 1, 5, "Composer", 280000, 1100000, 0.99),
    ]
    cursor.executemany("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tracks_data)
    
    employees_data = [
        (1, "Adams", "Andrew", "General Manager", None, "1962-02-18", "2002-08-14", "11120 Jasper Ave NW", "Edmonton", "AB", "T5K 2N1", "Canada", "+1 (780) 428-9482", "andrew@chinookmusic.com"),
        (2, "Edwards", "Nancy", "Sales Manager", 1, "1958-12-08", "2002-05-15", "825 8 Ave SW", "Calgary", "AB", "T2P 2T3", "Canada", "+1 (403) 262-3361", "nancy@chinookmusic.com"),
        (3, "Peacock", "Jane", "Sales Support Agent", 2, "1973-08-29", "2002-04-01", "1111 6 Ave SW", "Calgary", "AB", "T2P 5M5", "Canada", "+1 (403) 262-6712", "jane@chinookmusic.com"),
    ]
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", employees_data)
    
    customers_data = [
        (1, "Luís", "Gonçalves", "Embraer - Empresa Brasileira de Aeronáutica S.A.", "Av. Brasil, 2442", "São José dos Campos", "SP", "12227-000", "Brazil", "+55 (12) 3923-5555", "luisgoncalves@embraer.com.br", 3),
        (2, "Leonie", "Köhler", None, "Theodor-Heuss-Str. 34", "Stuttgart", None, "70174", "Germany", "+49 0711 2842410", "leonie.kohler@surfeu.de", 5),
        (3, "François", "Tremblay", None, "1498 rue Bélanger", "Montréal", "QC", "H2G 1A7", "Canada", "+1 (514) 721-4711", "ftremblay@gmail.com", 3),
        (4, "Bjørn", "Hansen", None, "Ullevålsveien 14", "Oslo", None, "0171", "Norway", "+47 22 44 85 88", "bjorn.hansen@yahoo.no", 4),
        (5, "Frédérique", "Chubin", None, "54, rue Royale", "Nantes", None, "44000", "France", "+33 2 40 46 40 46", "frederic.chubin@citromatic.fr", 3),
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", customers_data)
    
    invoices_data = [
        (1, 2, "2021-01-01", "Theodor-Heuss-Str. 34", "Stuttgart", None, "70174", "Germany", 1.98),
        (2, 4, "2021-01-02", "Ullevålsveien 14", "Oslo", None, "0171", "Norway", 3.96),
        (3, 1, "2021-01-03", "Av. Brasil, 2442", "São José dos Campos", "SP", "12227-000", "Brazil", 5.94),
        (4, 3, "2021-01-06", "1498 rue Bélanger", "Montréal", "QC", "H2G 1A7", "Canada", 1.98),
        (5, 5, "2021-01-11", "54, rue Royale", "Nantes", None, "44000", "France", 8.91),
    ]
    cursor.executemany("INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", invoices_data)
    
    invoice_items_data = [
        (1, 1, 1, 0.99, 1),
        (2, 2, 2, 0.99, 2),
        (3, 3, 3, 0.99, 2),
        (4, 4, 4, 0.99, 1),
        (5, 5, 5, 0.99, 3),
        (6, 5, 6, 0.99, 3),
    ]
    cursor.executemany("INSERT INTO invoice_items VALUES (?, ?, ?, ?, ?)", invoice_items_data)
    
    playlists_data = [
        (1, "Music Videos"),
        (2, "Grunge"),
        (3, "Classical 101 - Deep Cuts"),
        (4, "Heavy Metal Classics"),
        (5, "Jazz After Hours"),
    ]
    cursor.executemany("INSERT INTO playlists VALUES (?, ?)", playlists_data)
    
    media_types_data = [
        (1, "MPEG audio file"),
        (2, "Protected AAC audio file"),
        (3, "Protected MPEG-4 video file"),
        (4, "Purchased AAC audio file"),
        (5, "AAC audio file"),
    ]
    cursor.executemany("INSERT INTO media_types VALUES (?, ?)", media_types_data)
    
    # Commit and close
    conn.commit()
    conn.close()
    print(f"✅ Chinook database created at {db_path}")

if __name__ == "__main__":
    create_chinook_db()
