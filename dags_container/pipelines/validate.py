from pydantic import ValidationError
from config.settings import LOGGER

from validators.validators import ReservationValidator

logger = LOGGER

def validate(response):
    """
        Validates reservation data using the Pydantic ReservationValidator.

        This function processes the nested response dictionary containing reservation
        data for each platform and restaurant. It attempts to validate each reservation
        record using the ReservationValidator schema. Valid reservations are stored in
        the `validated_reservation` list, while invalid records (those raising a 
        ValidationError) are stored in the `validation_error_reservation` list.

        Args:
            response (dict): A nested dictionary of booking data in the format:
                            {
                                platform1: {
                                    restaurant1: [ {...reservation1...}, {...reservation2...}, ... ],
                                    ...
                                },
                                ...
                            }

        Returns:
            dict: A dictionary containing:
                - 'validated': list of validated reservations in JSON serialisable format
                - 'error': list of reservations that failed validation
    """
    logger.info('\n data entered transform pipe..')
    validated_reservation = []
    validation_error_reservation = []
    logger.info("Data passed on to validators....")
    for platform in response:
        for restaurant in response[platform]:
            for reservation in response[platform][restaurant]:
                try:
                    reservations = ReservationValidator(**reservation)
                    validated_reservation.append(reservations.model_dump(mode='json'))
                except ValidationError as e:
                    validation_error_reservation.append(reservation)
                    logger.error(f'An error occured: {e}')

    logger.info(f'Total Validated: {len(validated_reservation)}')
    logger.info(f'Errors in Validation: {len(validation_error_reservation)}')

    if len(validation_error_reservation)  != 0:
        logger.error(f'Error in validation. Error Count:{len(validation_error_reservation)}')

    return {
        'validated': validated_reservation,
        'error': validation_error_reservation
    }
    