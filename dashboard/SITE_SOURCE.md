# ForgeLab Control Plane source

Source imported from the ForgeLab Control Plane Site at commit
`ee731ab66a52fb650522feaadc4927f1c9c88925` and adapted for the M8.1 local
runner connection.

The local dashboard reads run artifacts through the loopback-only authenticated
ForgeLab API. A staged gate decision never promotes or modifies a repository.
