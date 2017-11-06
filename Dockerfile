FROM python:2.7
RUN apt-get update
RUN apt-get install -y apt-utils apt-transport-https
RUN apt-get -y upgrade
RUN wget -q -O - https://mkvtoolnix.download/gpg-pub-moritzbunkus.txt | apt-key add -
RUN echo "deb https://mkvtoolnix.download/debian/jessie/ ./" >> /etc/apt/sources.list.d/bunkus.org.list
RUN echo "deb-src https://mkvtoolnix.download/debian/jessie/ ./" >> /etc/apt/sources.list.d/bunkus.org.list
RUN echo "deb http://www.deb-multimedia.org jessie main non-free" >> /etc/apt/sources.list.d/multimedia.org.list
RUN echo "deb-src http://www.deb-multimedia.org jessie main non-free" >> /etc/apt/sources.list.d/multimedia.org.list
RUN apt-get update
RUN apt-get install -y --force-yes deb-multimedia-keyring
RUN apt-get update
RUN apt-get install -y mkvtoolnix ffmpeg
RUN pip install envoy enzyme mutagen tmdbsimple imdbpy python-dateutil
RUN mkdir -p /root/media/Avatar\ \(2009\)
ADD http://www.sample-videos.com/video/mkv/240/big_buck_bunny_240p_30mb.mkv /root/media
RUN mv /root/media/big_buck_bunny_240p_30mb.mkv /root/media/Avatar\ \(2009\).mkv
RUN mv /root/media/Avatar\ \(2009\).mkv /root/media/Avatar\ \(2009\)/
RUN git clone https://BinaryMisfit:XN78j6dBxx_rdoHsPinK@gitlab.com/senselessly_foolish/python_projects/movie_tools.git /root/movie_tools