
class LogSource(object):

    def log(self, msg, level):
        pass


class LogSink(object):

    def write_to_log(self):
        pass


""" TODO: ability to do this...
logger = Logger(settings.params.log_level, name="governor")
mp_sink = MultiprocessSink()
logger.chain(mp_sink)

demux_sink = DemuxSink()
print_sink = StreamSink(stream=sys.stdout)
demux_logger.add_route(gov_printer, name="governor")
mp_logger.chain(demux_logger)

copied_logger = logger.new(name="copied")                       # log source, inherits sinks (by ref)
"""
