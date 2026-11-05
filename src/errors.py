class IntegrationError(Exception):
    pass


class InvalidDataError(IntegrationError):
    pass


class ModuleUnavailableError(IntegrationError):
    pass


class IntegrationTimeoutError(IntegrationError):
    pass


class VersionConflictError(IntegrationError):
    pass
