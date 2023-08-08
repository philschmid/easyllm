import logging
import os
import sys


def setup_logger() -> logging.Logger:
    # get local rank
    local_rank = int(os.environ.get("LOCAL_RANK", 0))

    # create logger
    logger = logging.getLogger(__name__)

    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    if local_rank != 0:
        # disable logging for non-master processes
        print(f"Disabling logging for non-master process with local rank {local_rank}.")
        logging.disable(logging.CRITICAL)
        return logger
    else:
        log_level = logging.INFO
        # set the main code and the modules it uses to the same log-level according to the node
        logger.setLevel(log_level)
        # datasets_logging.set_verbosity(log_level)
        # trfs_logging.set_verbosity(log_level)
        return logger


logger = setup_logger()
