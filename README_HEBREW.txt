Tesla Telegram Alert - GitHub Actions - חינם

מה זה עושה?
המערכת בודקת את עמוד המלאי של טסלה ישראל כל 10 דקות.
אם יש שינוי בעמוד - היא שולחת התראה לטלגרם.

לינק שנבדק:
https://www.tesla.com/he_IL/inventory/new/my?PaymentType=cash

איך מתקינים?

1. פתח GitHub.
2. צור Repository חדש בשם:
   tesla-alert-bot

3. העלה את הקבצים האלה:
   - tesla_check.py
   - README_HEBREW.txt
   - התיקייה .github כולל הקובץ:
     .github/workflows/tesla-watch.yml

חשוב:
אם אתה מעלה דרך האתר של GitHub, צריך לגרור את כל התיקייה כמו שהיא.

4. ב-GitHub כנס ל:
   Settings > Secrets and variables > Actions > New repository secret

5. צור Secret ראשון:
   Name:
   TELEGRAM_BOT_TOKEN

   Value:
   הטוקן החדש שקיבלת מ-BotFather

6. צור Secret שני:
   Name:
   TELEGRAM_CHAT_ID

   Value:
   ה-chat id שלך

7. כנס ללשונית:
   Actions

8. תבחר:
   Tesla Inventory Watch

9. תלחץ:
   Run workflow

10. אם הכל תקין תקבל הודעה בטלגרם:
   Tesla Watch started

אחרי זה זה ירוץ אוטומטית כל 10 דקות.

הערה:
הגרסה הזו מזהה כל שינוי בעמוד.
לפעמים שינוי קטן באתר גם יכול לשלוח התראה.
אם תרצה בהמשך, אפשר לשדרג את זה לזיהוי מדויק של רכב חדש לפי דגם/מחיר/VIN.