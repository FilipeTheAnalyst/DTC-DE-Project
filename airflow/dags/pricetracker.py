import pandas as pd
import smtplib
from email.message import EmailMessage

def check_target_price(email_user, email_password, prices_file, wishlist_file, execution_date):
    df_prices = pd.read_csv(prices_file)
    df_wishlist = pd.read_csv(wishlist_file)

    df_final = pd.merge(df_prices, df_wishlist, on='id')

    for index, row in df_final.iterrows():
        if row['price_x'] <= row['price_y']:
            print('The game ',row['name'],' is below the price you wanted! Currently the price is ',row['price_x'],'€! Here is the link to buy: ',row['url'],'!!!')

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(email_user, email_password)
                print('E-mail pass: ',email_password)
                msg = EmailMessage()
                msg['Subject'] = f"{row['name']} is at {row['price_x']}€! Now is your chance to buy!"
                msg['From'] = email_user
                msg['To'] = email_user
                msg.set_content(f"Filipe, This is the moment we have been waiting for.\nNow is your chance to pick up {row['name']}.\nDon't mess it up! Link here: {row['url']}")
                smtp.send_message(msg)
                print('Message sent! Check your e-mail account!') 