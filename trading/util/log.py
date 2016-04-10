class Logger:
    logging_message = '[{level}], message: {message} data: {data}'

    def info(self, message, data):
        log_level = 'INFO'
        print(self.logging_message.format(level=log_level, message=message, data=data))

    def error(self, message, data):
        log_level = 'ERROR'
        print(self.logging_message.format(level=log_level, message=message, data=data))

    def debug(self, message, data):
        log_level = 'DEBUG'
        print(self.logging_message.format(level=log_level, message=message, data=data))