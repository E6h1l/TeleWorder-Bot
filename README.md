# Teleworder
This Telegram bot will help you learn words of any language. 

The entire bot interface is in Ukrainian.

Click to try:  **[@TeleWorder_bot](https://t.me/TeleWorder_bot)**

## How to run Bot
___

First of all you need to file named **'database name'.db**

```
touch 'database_name'.db
```
Set environment variables `API_TOKEN_TELEWORDER` and `DB_PATH`
```
export API_TOKEN_TELEWORDER='Your_API_Token'
```
```
export DB_PATH='Path_to_"database_name".db'
```

After that  run `main.py`:
```
python main.py
```

## Example of use
___

The user does not know how to translate the word `sun` in Ukrainian.\
In order to learn the word, he starts the bot, after which a menu with commands will appear.\
To add a new word, you need to write the command `/new` and input word and word translation through a space:
> sun сонце 

After the user has added all the words he wants to learn, the user can enable the sending of all the added words with a period of 10 minutes, 15 minutes, 30 minutes or an hour. Use command `/on` and `/off` to turn off notifications <br>

After that, the user's words will be sent in turn with the selected period

If the user has learned the word, he can delete it using the command `/remove` .\
After that, he will need to enter the translation of the word, or the original word:
>sun

or

>сонце

Good use :relieved:

## Author
___
### **[Dmytro Prystaichuk ( E6H1L )](https://github.com/E6h1l)**
