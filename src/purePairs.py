from Config import get_config
import string
config = get_config()


if __name__ == '__main__':
    fs = [
        'Cell_Phones_and_Accessories',
        'Electronics',
        'Baby',
        'Health_and_Personal_Care',
        'Digital_Music']

    noisePairs = {}
    for f in fs:
        pairs = []
        with open(config.data_path + f + '/' + f +'_pairs_freq.txt', 'r') as files:
            print f
            for line in files:
                parts = line.split(' ', 1)
                parts[1] = parts[1][:-2]
                # print parts[1]
                if int(parts[1]) < 100:
                    break ;
                parts[0] = parts[0].translate(None, string.punctuation)
                if parts[0][0] == '1':
                    pairs.append(parts[0][1:])
            files.close()
            print pairs
        noisePairs[f] = pairs

        with open(config.data_path + f + '/' + f + '_Pairs_IDSET.txt', 'r') as files:
            a = []
            for line in files:
                sig = 0
                for pair in pairs:
                    if pair in line:
                        sig = 1
                        break;
                if sig==0:
                    a.append(line)
            files.close()

        with open(config.data_path + f + '/' + f + '_pairs_IDSET_removed.txt', 'w') as files:
            for str in a:
                files.write(str)
            files.close()

        with open(config.data_path + f + '/' + f + '_pairs.txt', 'r') as files:
            a = []
            for line in files:
                sig = 0
                for pair in pairs:
                    if pair in line:
                        sig = 1
                        break;
                if sig == 0:
                    a.append(line)
            files.close()

        with open(config.data_path + f + '/' + f + '_pairs_removed.txt', 'w') as files:
            for str in a:
                files.write(str)
            files.close()


