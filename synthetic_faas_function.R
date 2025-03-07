synthetic_faas_function <- function(folder, execution_time, input_files, output_size_in_bytes) {

    #Download input files from S3
    for(file in input_files) {
        tryCatch({
            faasr_log(paste0("Downloading file: ", file))
        faasr_get_file(remote_folder=folder, remote_file=file, local_file=tempfile(pattern=file, fileext='.txt'))
        }, error = function(e) {
            faasr_log(paste0("ERROR: Failed to download: ", file))
            stop(e)
        }
        )
    }

    #Simulate functions execution
    Sys.sleep(execution_time)

    #Open a binary connection for output file
    output_file <- tempfile(pattern="output", fileext=".bin")
    con <- file(output_file, "wb")
    on.exit(close(con))

    # Moves file pointer to output_size_in_bytes - 1 and writes a byte to file
    seek(con, where = output_size_in_bytes - 1)
    writeBin(as.raw(0), con)

    #Store output file in S3
    faasr_put_file(local_file=output_file, remote_folder=folder, remote_file=output_file)

    #Log function
    log_msg <- paste0('Function synthetic_faas_function finished; output written to ', folder, '/', output_file, ' in default S3 bucket')
    faasr_log(log_msg)
}
