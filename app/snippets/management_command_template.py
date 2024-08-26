from django.core.management.base import BaseCommand
import logging
import inspect
import time
from shared.models import CommandException
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):

    def handle(self, *args, **options):
        exception_count = 0
        start_time = time.time()

        moneysync_logger = logging.getLogger(__name__)
        exception_logger = logging.getLogger("exceptions")

        moneysync_logger.info(
            "----------------------------------------------------------------------------------------------------------------------------------------------------"
        )

        current_function_name = inspect.currentframe().f_code.co_name
        try:
            ...


        except Exception as e:
            exception_count += 1
            exception_logger.error(
                f"exception happened in Package:{__package__} Module:{__name__} Function:{current_function_name}(): {e}"
            )

        end_time = time.time()
        duration = end_time - start_time
        moneysync_logger.info(f"Synced in {duration:.2f} seconds")
        if exception_count > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"Synced with {exception_count} exceptions in {duration:.2f} seconds"
                )
            )

            command_exception = CommandException(
                command=__name__, count=exception_count
            )
            command_exception.save()
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Synced without exception in {duration:.2f} seconds"
                )
            )
