"""
Do batch preprocessing required for training.
Renaming files
"""

import os
import glob
import shutil  # to copy items


def renameFiles(input_dir='./recordings/', newBasename=""):
    """
    Rename all files

    Naming convetion:
        audiofilename__1.wav
        audiofilename__2.wav

    :param input_dir:
    :return:
    """

    # Make sure that the input_dir exists
    if not os.path.exists(input_dir):
        print("input_dir doesn't exists ", input_dir)
    assert os.path.exists(input_dir)

    files = glob.glob(os.path.join(input_dir, '*.*'))
    basenames = [os.path.basename(filename) for filename in files]
    baseDir = input_dir.split('/')[-1]

    sep = '__'
    basenames = sorted(basenames, reverse=True)
    for name in basenames:
        script, line = name.split('__')
        line, format = line.split('. ')
        # line = int(line) - 1
        # line = str(line)
        line = line + "." + format
        script = script.replace(' ', '')

        # For changing pagalbasti to pagalbasti01 or so
        if newBasename != "":
            script = newBasename

        new_name = '{}__{}'.format(script, line)
        print(os.path.join(input_dir, name), new_name)
        os.rename(os.path.join(input_dir, name), os.path.join(input_dir, new_name))


def rename_dir(input_dir='./recordings'):
    """
    Rename all the directories holding recordings
    :param input_dir:
    :return:
    """

    # Make sure the input dir exists
    if not os.path.exists(input_dir):
        print('Make sure input directory exists')
    assert os.path.exists(input_dir)

    # Make list of dirs inside the input_dir
    listOfDirs = os.listdir(input_dir)

    # renamed_dir = [dir.split('__')[0] for dir in listOfDirs]
    # print(renamed_dir)
    for dir in listOfDirs:
        newname = dir.split('__')[0]
        print(dir, newname)
        os.rename(os.path.join(input_dir, dir), os.path.join(input_dir, newname))
        # return renamed_dir


def makeSpeechRecognitionDataset(audio_dir='dataset3/audio', script_dir='dataset3/scripts',
                                 output_filename='dataset3/transcript.txt'):
    """
    If an audio file repeats, rename it
    Audio__line__1.wav -> audio__line__1__copy2.wa

    output : .fileids
    :param input_dir:
    TODO: Clean text and expand text
    """
    from collections import Counter

    # Checking if the audio dir and script dir exist or not.
    assert os.path.exists(audio_dir)
    assert os.path.exists(script_dir)

    # All the transcripts will be saved in this file
    # output_filename = os.path.join(audio_dir, output_filename)
    output_transcript_file = open(output_filename, mode='w', encoding='utf8')
    fileid = open(os.path.join(audio_dir, '.fileids'), mode='w', encoding='utf8')

    # Find all the audio dirs
    audio_record_dirs = os.listdir(audio_dir)

    # # Make filenames unique
    # list_of_dirs = [dir.split('__')[0] for dir in audio_record_dirs]
    # count_of_dirs = Counter(list_of_dirs)
    # # Find corresponding text file
    # text_files = [name + '.txt' for name in count_of_dirs.keys()]
    # for index, dir in enumerate(audio_record_dirs):
    #     base, ext = dir.split('__')[0], dir.split('__')[1:]
    #     count = count_of_dirs[base]
    #
    #     # Do not change anything if just a single copy exists
    #     if count == 1:
    #         continue
    #     count_of_dirs[base] = count - 1
    #
    #     newBasename = base + str(count_of_dirs[base])
    #     newdir = newBasename + '__' + '__'.join(ext)
    #
    #     old_scriptname = os.path.join(script_dir, base + '.txt')
    #     new_scriptname = os.path.join(script_dir, newBasename + '.txt')
    #     shutil.copy(old_scriptname, new_scriptname)
    #
    #     old_audiodir = os.path.join(audio_dir, dir)
    #     new_audiodir = os.path.join(audio_dir, newdir)
    #     os.rename(src=old_audiodir, dst=new_audiodir)
    #     renameFiles(new_audiodir, newBasename=newBasename)
    #
    #     print(index, dir, newdir)
    #     print(index, old_scriptname, new_scriptname)


    # Look for the script corresponding to audio_dirs
    for index, record_dir in enumerate(audio_record_dirs):

        # Find all the wav files in audio dir
        audio_files = glob.glob(os.path.join(os.path.join(audio_dir, record_dir), '*.wav'))

        # Make sure the audio directory is not empty
        if not len(audio_files):
            print('Encountered empty directory {}'.format(record_dir))
            continue

        # Generate corresponding script filename
        if '__' in record_dir:
            record_dir = record_dir.split('__')[0]
        script_name = os.path.join(script_dir, record_dir + '.txt')

        # If script file corresponding to audio folder doesn't exist, abandon the audio file
        if not os.path.exists(script_name):
            print('*********************Script file {} does not exist'.format(script_name))
            continue

        # Read script and split in into lines
        text = open(script_name, encoding='utf8', mode='r').read().split('\n')

        print('No of text lines in {} : {} '.format(script_name, len(text)))
        print("Script Name : ", script_name)

        # Match text_line to audio_line / audio_recording
        script_name = os.path.basename(audio_files[0]).split('__')[0]

        for audio_linename in audio_files:
            # Determine the line number to retrieve corresponding text
            line_number = audio_linename.split('__')[-1]
            line_number = int(line_number.split('.')[0])

            audio_linename = '{}__{}'.format(script_name, str(line_number))
            text_line = '<s> {}  </s> ({})\n'.format(text[line_number], audio_linename.split('.')[0])

            # print(text_line, new_audio_name)
            output_transcript_file.write(text_line)

            fileid_line = '{}/{}\n'.format(script_name, audio_linename.split('.')[0])
            fileid.write(fileid_line)

    output_transcript_file.close()
    fileid.close()


def makeHotWordRecognitionDatset(pos_word="Ferry", audio_dir='dataset3/audio', transcript_name='dataset3/scripts',
                                 pos_dir='dataset3/', neg_dir='dataset3/', audio_format="mp3"):
    """
    Keep all the positive hot words in /pos/ directory.
    Keep all other words in /neg/ directory
    Format : wav, mp3, ogg. Skip . or *
    """

    # Checking if the audio dir exist or not. If output dirs do not exist, make one.
    assert os.path.exists(audio_dir)
    if not os.path.exists(pos_dir):
        os.makedirs(pos_dir)
    if not os.path.exists(neg_dir):
        os.makedirs(neg_dir)

    pos_word = pos_word.lower()

    # Look for the script corresponding to audio_dirs
    text = open(file=transcript_name, mode='r', encoding='utf8').read().lower().split('\n')
    audio_files = glob.glob(os.path.join(audio_dir, "*." + audio_format))
    for audio_linename in audio_files:
        # Determine the line number to retrieve corresponding text
        line_number = audio_linename.split('__')[-1]
        line_number = int(line_number.split('.')[0])
        if text[line_number] == pos_word:
            new_name = os.path.join(pos_dir, os.path.basename(audio_linename))
            # print("pos ", os.path.basename(audio_linename))
            # Save in pos directory
        else:
            # Save the audio in neg directory
            new_name = os.path.join(neg_dir, os.path.basename(audio_linename))
            # print("neg", os.path.basename(audio_linename))
        os.rename(audio_linename, new_name)


def makeSpeechSynthesisDataset(audio_dir='', script_dir='./scripts'):
    """
    audio_dir: dir containing dirs of audio recordings
    script_dir: dir containing scripts

    If an audio file repeats, rename it
    Audio__line__1.wav -> audio__line__1__copy2.wa

    Determine copy
        Make a list of text files read. And count the occurence.

    :return: transcript.txt in audio_dir and renamed audio files
    """

    # Checking if the audio dir and script dir exist or not.
    assert os.path.exists(audio_dir)
    assert os.path.exists(script_dir)

    # All the transcripts will be saved in this file
    output_transcript_name = os.path.join(audio_dir, 'transcript.txt')
    output_transcript_file = open(output_transcript_name, mode='w', encoding='utf8')

    # To count the occurence of scripts
    list_scripts = []

    # Find all the audio dirs
    audio_record_dirs = os.listdir(audio_dir)
    audio_count = 0

    print(audio_record_dirs)
    # Look for the script corresponding to audio_dirs
    for index, record_dir in enumerate(audio_record_dirs):

        # Find all the wav files in audio dir
        audio_files = glob.glob(os.path.join(os.path.join(audio_dir, record_dir), '*.wav'))

        # Make sure the audio directory is not empty
        if not len(audio_files):
            print('Encountered empty directory {}'.format(record_dir))
            continue

        # Generate corresponding script filename
        if '__' in record_dir:
            record_dir = record_dir.split('__')[0]
        script_name = os.path.join(script_dir, record_dir + '.txt')

        # If script file corresponding to audio folder doesn't exist, abandon the audio file
        if not os.path.exists(script_name):
            print('Script file {} does not exist'.format(script_name))
            continue

        # Read script and split in into lines
        text = open(script_name, encoding='utf8', mode='r').read().split('\n')

        print('No of text lines in {} : {} '.format(script_name, len(text)))
        print("Script Name : ", script_name)

        # Match text_line to audio_line / audio_recording
        script_name = os.path.basename(audio_files[0]).split('__')[0]

        # Find if the file been read before
        list_scripts.append(script_name)
        reading_count = list_scripts.count(script_name)
        if reading_count > 1:
            script_name += '__Copy' + str(reading_count)
            # TODO: We'll make changes in this section later. For now we will just skip
            continue

        for audio_linename in audio_files:
            # Determine the line number
            line_number = audio_linename.split('__')[-1]
            line_number = int(line_number.split('.')[0])

            new_audio_name = 'nepali__{}.wav'.format(str(audio_count))
            text_line = '( {} "{}" )\n'.format(new_audio_name.split('.')[0], text[line_number])
            audio_count += 1

            new_audio_name = os.path.join(audio_dir, new_audio_name)
            # print(text_line, new_audio_name)
            output_transcript_file.write(text_line)
            os.rename(audio_linename, new_audio_name)

    output_transcript_file.close()


if __name__ == "__main__":
    audio_dir = './dataset3/audio'
    script_dir = './dataset3/scripts'
    audio_dir = '../recording/names'
    script_dir = '../recording/names.txt'

    # makeSpeechRecognitionDataset(audio_dir=audio_dir, script_dir=script_dir, output_filename='./names/transcript.txt')
    makeHotWordRecognitionDatset(pos_word="Ginger", audio_dir=audio_dir, transcript_name=script_dir,
                                 pos_dir="../recording/pos", neg_dir="../recording/neg")
    # makeSpeechSynthesisDataset(audio_dir='./synthesis/audio/',script_dir='./synthesis/scripts/')
    # input_path = './audio'
    # folders = os.listdir('./audio/')

    # renameFiles(input_dir='./dataset3/audio/Constitution2127')
    pass
