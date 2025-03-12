synthetic_faas_function <- function(folder, execution_time, input_files, input_size_in_bytes, output_size_in_bytes, actionid) {
    options(digits.secs = 6)

    time_stamp1 <- paste0('LOG DOWNLOAD[', actionid, '][',input_size_in_bytes,'][START]: began downloading files from S3 at time: ', format(Sys.time(), "%Y%m%d%H%M%OS6"))
    #Download input files from S3
    for(file in input_files) {
        tryCatch({
            faasr_log(paste0("Downloading file: ", file))
        faasr_get_file(remote_folder=folder, remote_file=file, local_file=paste0(format(Sys.time(), "%Y%m%d%H%M%OS6"), "-", file))
        }, error = function(e) {
            faasr_log(paste0("ERROR: Failed to download: ", file))
            stop(e)
        }
        )
    }
    time_stamp2 <- paste0('LOG DOWNLOAD[', actionid, '][',input_size_in_bytes,'][FINISH]: finished downloading files from S3 at time: ', format(Sys.time(), "%Y%m%d%H%M%OS6"))

    #Simulate functions execution
    time_stamp3 <- paste0('LOG SLEEP[', actionid, '][',execution_time,'][START]: began sleeping at time: ', format(Sys.time(), "%Y%m%d%H%M%OS6"))
    Sys.sleep(execution_time)
    time_stamp4 <- paste0('LOG SLEEP[', actionid, '][',execution_time,'][FINISH]: finished sleeping at time: ', format(Sys.time(), "%Y%m%d%H%M%OS6"))

    #Create binary file for output
    output_file <- tempfile(pattern="output", fileext=".bin")
    con <- file(output_file, "wb")
    on.exit(close(con))

    # Moves file pointer to output_size_in_bytes - 1 and writes a byte to file
    seek(con, where = output_size_in_bytes - 1)
    writeBin(as.raw(0), con)

    #Store output file in S3
    time_stamp5 <- paste0('LOG OUTPUT[', actionid, '][',output_size_in_bytes,'][START]: began transferring output file to S3 at time: ', format(Sys.time(), "%Y%m%d%H%M%OS6"))
    faasr_put_file(local_file=output_file, remote_folder=folder, remote_file=output_file)
    time_stamp6 <- paste0('LOG OUTPUT[', actionid, '][',output_size_in_bytes,'][FINISH]: finished transferring output file to S3 at time: ', format(Sys.time(), "%Y%m%d%H%M%OS6"))

    #Log function
    log_msg <- paste0('Function synthetic_faas_function finished; output written to ', folder, '/', output_file, ' in default S3 bucket')
    faasr_log(log_msg)
    faasr_log(time_stamp1)
    faasr_log(time_stamp2)
    faasr_log(time_stamp3)
    faasr_log(time_stamp4)
    faasr_log(time_stamp5)
    faasr_log(time_stamp6)
}