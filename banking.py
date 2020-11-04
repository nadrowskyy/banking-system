import random
from math import ceil
import sqlite3
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS card (
                id INTEGER NOT NULL,
                number TEXT NOT NULL,
                pin TEXT NOT NULL,
                balance INTEGER DEFAULT 0
                );''')
conn.commit()

class BankingSystem:
    id = 1

    def __init__(self):
        self.card_number = ""
        self.pin = ""
        self.balance = 0
        BankingSystem.id += 1

    def luhn_alghoritm(self, cn):
        '''Algorytm Luhn'a
        # 1 Ostatnia pozycja wypada (tego nie musimy robić bo przekazaliśmy do tej funkcji
        # numer bez ostatniej cyfry)
        # 2 Nieparzyste pozycje *2
        # Jeśli cyfra >9 odejmuemy 9
        # Dodać wszystkie cyfry i podzielić modulo10 czyli suma kontrolna'''

        # zamieniam cn na listę l gdzie elementami są cyfry karty
        luhn = [int(x) for x in cn]
        # nieparzyste miejsca *2, w pętli są parzyste ale to dlatego, że indeksujemy od zera!
        for i in [0, 2, 4, 6, 8, 10, 12, 14]:
            luhn[i] *= 2
        # odejmuje 9 od cyfr większych od 9
        luhn = [x-9 if x>9 else x for x in luhn]
        # suma luhn zaokrąglona do najwyższej 10 (czyli np. 41=50, 44=50) minus suma luhn da nam sumę kontrolną
        return int(ceil(sum(luhn)/10.0))*10 - sum(luhn)

    def create_card(self):
        # 15-cyfrowy numer karty, dla niego zastosujemy algorytm Luhn'a żeby wygenerować ostatnią cyfrę
        # Numer karty zaczynamy od 400000 bo takie jest założenie w projekcie
        card_number_15 = '400000' + str(random.randint(100000000, 999999999))
        self.card_number = str(card_number_15 + str(self.luhn_alghoritm(card_number_15)))
        self.pin = str(random.randint(1111, 9999))
        cur.execute("INSERT INTO card (id, number, pin) VALUES ({}, {}, {})".format(BankingSystem.id, self.card_number, self.pin))
        conn.commit()
        print("Your card has been created\nYour card number:\n{}\nYour card PIN:\n{}".format(self.card_number, self.pin))

    def login(self):
        print("Enter your card number:")
        card_number = input()
        print("Enter your PIN:")
        pin = input()
        cur.execute("SELECT number, pin FROM card WHERE number = {}".format(card_number))
        account = cur.fetchone()
        if account is not None:
            if account[0] == card_number and account[1] == pin:
                print("You have successfully logged in!")
                self.card_number = card_number
                self.pin =  pin
                self.panel()
            else: print("Wrong card number or pin")
        else: print("Wrong card number or pin")

    def panel(self):
        while True:
            cur.execute("SELECT * FROM card WHERE number = {}".format(self.card_number))
            panel_account = cur.fetchone()
            print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
            choice = int(input())
            if choice == 1:
                print("Balance: {}".format(panel_account[3]))
            elif choice == 2:
                print("Enter income")
                income = int(input())
                cur.execute("UPDATE card SET balance = balance + {} WHERE number = {}".format(income, self.card_number))
                conn.commit()
                self.balance += income
                print("Income was added!")
            elif choice == 3:
                print("Transfer\nEnter card number:")
                card_number_transfer = input()
                if card_number_transfer != self.card_number:
                    if card_number_transfer == (card_number_transfer[:15] + str(self.luhn_alghoritm(card_number_transfer[:15]))):
                        cur.execute("SELECT number FROM card WHERE number = {}".format(card_number_transfer))
                        number = cur.fetchone()
                        if number is not None:
                            if card_number_transfer == number[0]:
                                print("Enter how much money you want to transfer")
                                money_to_transfer = int(input())
                                if money_to_transfer < self.balance:
                                    cur.execute("UPDATE card SET balance = balance + {} WHERE number = {}".format(money_to_transfer, card_number_transfer))
                                    conn.commit()
                                    cur.execute("UPDATE card SET balance = balance - {} WHERE number = {}".format(money_to_transfer, self.card_number))
                                    conn.commit()
                                    print("Succes!")
                                else: print("Not enough money!")
                            else: print("Such card does not exist")
                        else: print("Such card does not exist")
                    else: print("Probably you made mistake in the card number. Please try again!")
                else: print("You can't transfer money to the same account!")
            elif choice == 4:
                cur.execute("DELETE FROM card WHERE number = {}".format(self.card_number))
                conn.commit()
                print("The account has been closed!")
                break
            elif choice == 5:
                print("You have successfully logged out!")
                break
            elif choice == 0:
                print("Bye!")
                exit(0)

newcard = BankingSystem()
while True:
    print('''1. Create an account
2. Log into account
0. Exit''')
    choice1 = int(input())
    if choice1 == 1:
        newcard.create_card()
    elif choice1 == 2:
        newcard.login()
    elif choice1 == 0:
        break

conn.close()
