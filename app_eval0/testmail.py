# import smtplib

# server = smtplib.SMTP('smtp.mailtrap.io', 587)
# server.starttls()
# server.login('00e6a449eebca0', '17ba0cc043289c')
# server.sendmail('JospinBomo@teccart.com', 'bnjabnja04@gmail.com', 'Test email')
# server.quit()


import smtplib

try:
    server = smtplib.SMTP('smtp.mailtrap.io', 587)  # Essayez le port 2525 si 587 ne fonctionne pas
    server.starttls()
    server.login('00e6a449eebca0', '17ba0cc043289c')
    message = 'Subject: Test\n\nThis is a test email'
    server.sendmail('JospinBomo@teccart.com', 'bnjabnja04@gmail.com', message)
    print("E-mail envoyé avec succès")
except smtplib.SMTPException as e:
    print("Erreur lors de l'envoi de l'e-mail :", e)
finally:
    server.quit()
