from xos.logger import Logger, logging, logger


class ErrorMapper:
    def __init__(self, error_map_file):
        self.error_map = {}

        ## andrew   set default entry
        self.error_map['0'] = "ok"
        self.error_map['1'] = "processing"

        try:
            error_map_lines = open(error_map_file).read().splitlines()
            for l in error_map_lines:
                if (not l.startswith('#')):
                    splits = l.split('->')
                    k, v = map(lambda i: i.rstrip(), splits)
                    self.error_map[k] = v
        except Exception,e:
            logging.info('Could not read error map: %s' % str(e))

    def map(self, error):
        return self.error_map[error]
