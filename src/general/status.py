class Status:
    def __init__(self, error_code=None, message=None):
        self.errorCode = error_code
        self.message = message

    def tuple_response(self):
        return self.errorCode, self.message

    @classmethod
    def custom_status(cls, msg):
        return cls(400, msg)

    @classmethod
    def something_went_wrong(cls):
        return cls(400, 'Something went wrong')

    @classmethod
    def successfully_processed(cls):
        return cls(200, 'Successfully processed')

    @classmethod
    def access_denied(cls):
        return cls(400, 'Access denied')

    @classmethod
    def user_not_exists(cls):
        return cls(400, 'This user does not exist')

    @classmethod
    def activity_not_exists(cls):
        return cls(400, 'This activity does not exist')

    @classmethod
    def please_select_user(cls):
        return cls(400, 'Please select user')

    @classmethod
    def user_already_exists(cls):
        return cls(400, 'This user already exists')

    @classmethod
    def email_already_exists(cls):
        return cls(400, 'This email is already registred')

    @classmethod
    def email_not_exists(cls):
        return cls(404, 'E-Mail not registred. Provide valid e-mail address.')

    @classmethod
    def login_failed(cls):
        return cls(404, 'Login data is incorrect')

    @classmethod
    def user_not_activated(cls):
        return cls(404, 'This user is not activated')

    @classmethod
    def passwords_are_incorrect(cls):
        return cls(400, 'Passwords are incorrect ')

    @classmethod
    def username_already_taken(cls):
        return cls(400, 'This username is already taken')

    @classmethod
    def user_already_activated(cls):
        return cls(400, 'This user is already activated')

    @classmethod
    def email_already_taken(cls):
        return cls(400, 'This email is already taken')

    @classmethod
    def password_is_incorrect(cls):
        return cls(404, 'Old password is incorrect')

    @classmethod
    def mail_cannot_be_empty(cls):
        return cls(400, 'Mail can not be empty')

    @classmethod
    def can_not_self_deactivate(cls):
        return cls(400, 'You are not allowed to deactivate your account')

    @classmethod
    def property_doesnot_exists(cls):
        return cls(400, 'Property does not exists')

    @classmethod
    def property_deactivated(cls):
        return cls(400, 'Property does not exists')

    @classmethod
    def property_active(cls):
        return cls(400, 'Property is already active')

    @classmethod
    def property_sold(cls):
        return cls(400, 'Property sold')

    @classmethod
    def sale_doesnt_exists(cls):
        return cls(400, "Sale doesn't exists")

    @classmethod
    def property_owner_id_not_exists(cls):
        return cls(400, 'Property owner does not exists')


    @classmethod
    def user_is_owner(cls):
        return cls(400, 'This buyer owns property')