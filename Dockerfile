FROM python:2.7
RUN mkdir -p /root/media
ADD http://www.sample-videos.com/video/mkv/240/big_buck_bunny_240p_30mb.mkv /root/media/
RUN mv /root/media/big_buck_bunny_240p_30mb.mkv /root/media/Avatar\ \(2009\).mkv
RUN git clone https://BinaryMisfit:XN78j6dBxx_rdoHsPinK@gitlab.com/senselessly_foolish/python_projects/movie_tools.git /root/movie_tools