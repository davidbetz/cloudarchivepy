# CloudArchive for Python

**Copyright (C) 2016-2017 David Betz**

![logo](https://jampadcdn01.azureedge.net/common/images/db/cloudarchive.svg)

Tool to automate asset modification, mirroring to Azure or S3, and tracking via mongo/elastic/azure-table-storage.

In addition to basic blob transfer, this tool provides three more major features:

 * tracking database - uploaded blobs can be added to a database for easy tracking (e.g. your website can read from it)
 * econtent awareness - [econtent](https://github.com/davidbetz/econtent) is a project of mine used to add metadata to content and to make content multidimentional
 * middleware - blobs can be updated based on custom logic before uploading (utilizes my [middleware](https://github.com/davidbetz/middleware) project)
 
You point it at folders, stuff is mirrored to Azure/S3. The system keeps track of what's new, so only new stuff is sent.

See below Example Scenario section for an end-to-end scenario.

**This is fairly non-trivial project, so if you like it, feel free to send me bitcoin, or contact me about donating free conference tickets or something.**

## Config

First, you create storage config (with keys). Then, you create "areas" with a name (simply) for output, a folder (the branch you want to mirror), what storage config you want (created from previous step), what file types you want to scan for (sometimes you'll want zip/rar to one storage system and images to a different one), and, optionally, what remote branch you want the entire thing put under.

Basically, do the following...

    storageAccounts:
        - name: cloudarchive01
          provider: azure
          key1: AZURE_KEY_HERE
          key2: azure only uses key 1
            
        - name: cloudarchive02
          provider: s3
          key1: S3_ACCESS_KEY_HERE
          key2: S3_ACCESS_SECRET_HERE
      
    areas:
      - name: book_images
        folder: /var/archive/_BOOK
        container: books
        remoteBranch: images
        storage: cloudarchive01
        fileTypes:
            - extension: png
            - extension: svg
            - extension: jpg
            - extension: jpeg
            - extension: gif
              
      - name: book_text
        folder: /var/archive/_BOOK
        container: books
        remoteBranch: text
        storage: cloudarchive01
        fileTypes:
            - extension: txt
      
      - name: mp3
        folder: /var/archive/_AUDIOTEST
        container: mp3
        storage: cloudarchive01
        fileTypes:
            - extension: mp3
           
      - name: archives
        remoteBranch: misc
        container: s3 does not use container; use remoteBranch for a remote folder
        folder: /var/archive/_ARCHIVETEST
        storage: cloudarchive02
        fileTypes:
            - extension: zip
            - extension: rar
            - extension: gz
          
In this example, I'm searching a book folder (personally, I scan and OCR most of my books), and putting the raw images in one place and the OCRed text files in another. A common senario might be to put images in photo album backups in one place and home videos in another. In the above scenario, they are in the same storage account, but in different folders, they could just as easily be put in different ones (hot storage and cool storage), or just in different containers (private and public or just two for the sake of two).

## Usage
        
You run this with this:

    python cloudarchive.py -a <area_name>

But this will only do a dry run to show you what will happen. To run for real:

    python cloudarchive.py -a <area_name> -l

Get itemized output with the -v option:

    python cloudarchive.py -a <area_name> -l -v

Updates are done incrementally, so if you change targets or need to do a full-update for some reason, add `-f`:

    python cloudarchive.py -a <area_name> -l -f

Basically just look at the command line options.

## Optimization
        
A local .dates.json file is created to optimize uploads. The system will check hashes to see if the file changed. This also means updates are incremental (only new or updates files are uploaded). You can invalidate a single file by modifying its entry in the file or you can do a full upload with the -f command line option.

Note: if you change the storage config, you'll have to run with -f or else the system will think nothing has changed. Which makes sense, because nothing has.

## Sensitive Keys

Because putting sensitive information in config files is stupid, you can put your key in a file and simply reference the file name in ().

Basically:

    storageAccounts:
        - name: cloudarchive01
          provider: azure
          key1: (/srv/_cert/cloud/azure_key)
          key2: azure only uses key 1
            
        - name: cloudarchive02
          provider: s3
          key1: (/srv/_cert/cloud/s3_access_key_id)
          key2: (/srv/_cert/cloud/s3_shared_access_key)

##  Example Scenario

Imagine the following:

### Scenario

You have a series of podcasts which you want to show on your website. Podcasts are based on MP3s. MP3s have ID3 tags. You need to make sure the ID3 tags are up to date. You're smart, therefore don't want a lot of steps. You want to throw the files somewhere, give it metadata, and be done with it.

### Storage

The most fundamental component of the system (the sine qua non) is the blob store interaction (I'll normally refer to this as an asset store, since that's more accurate).

In this example, we have a `/var/audio/book/jdoe/analysis` folder with the following [fictional] pompous-sounding titles:
    
    01 - Introduction.mp3
    02 - 1 Locke on the Analysis of the Establishments.mp3
    03 - 2 The Government Controversies.mp3
    04 - 3 The Intellectual Shape of the Compliance Debates.mp3
    05 - 4 Identity, Distinction, or Tension in Non-Establishment Language.mp3
    06 - 5 Tension in Distinction.mp3
    07 - 6 The Irreducible Extensiveness of Systems.mp3

As you'll see in the later docs, you setup the creds in config. In this example we have the following config areas:
    
    trackingAccounts:
        - name: mongo01
          provider: mongo
          location: (/srv/_cert/cloud/mongo_location)
          key1: (/srv/_cert/cloud/mongo_username)
          key2: (/srv/_cert/cloud/mongo_password)
    
    storageAccounts:
        - name: azure01
          provider: azure
          key1: (/srv/_cert/cloud/azure_key)
          key2: azure only uses key 1
    
    areas:
      - name: audiobooks
        folder: /var/audio/book
        container: audio
        storage: azure01
        tracking: mongo01
        fileTypes:
            - extension: mp3

Again, you're smart, so your creds aren't in a place that's going to be committed to any version control system-- they are on the target systems. In this case your creds are in places like `/srv/_cert/cloud/mongo_username`.

With only the `areas:` and `storageAccounts:` config, cloudarchive would know to mirror all mp3 files in the entire local branch to azure in a folder named `audio`.

### Tracking

The existence of the `trackingAccounts:` config with the `tracking: mongo01` config means that the assets will added into a table/collection in the stated database.

This allows you to query your assets from your website or whereever else.

As of right now, Azure Table Storage, MongoDB, and ElasticSearch providers are included with cloudarchive.

### ID3 Tags

Using the middleware feature, you can add a preprocessor to ensure your ID3 tags are correct before uploading. This exact example is already provided with [content_middleware.py](content_middleware.py) and econtent-awareness.

Now, in that same podcast/audiobook folder, you might include the following `.manifest` file:
    
    @author@ John Doe
    @album@ Analysis of non-establishment systems for extensive compliance systems
    @track@ {{Name|([0-9]+) - (.*)\.mp3|$1}}
    @title@ {{Name|([0-9]+) - (.*)\.mp3|$2}}

When cloudarchive runs, each MP3's ID3 tag will be updated with the correct author and album. In addition, the filename will be parsed via regex to set the track # and the individual title.

In a podcast, you often want to set this data per-item (e.g. for guest speakers). In this example, though, we will assume the book author is the editor, and each chapter has its own author. So, in addition to the above, you may want to add the following file to tweak the metadata for one mp3 by adding the following `.03 - 2 The Government Controversies.mp3.manifest' file:

    @album@ Jame Smith
    
This is all done before any uploading is done.

Obviously, the change of a manifest, implies a change in a file. Thus, the original file is invalidated, telling cloudarchive that it needs to be uploaded.

In the end, we have the following in Azure:

![Settings Azure](https://raw.githubusercontent.com/davidbetz/cloudarchivepy/master/docs/images/azure-blob-storage.png)

We also have this in our MongoDB database (since the provider was MongoDB):
        
    > db.mp3.find()
    { "_id" : ObjectId("57b77879e138236271ac5bd4"), "album" : "Analysis of non-establishment systems for extensive compliance systems", "hash" : "lZyECLS2BP6XTPLm2ulPXg==", "author" : "John Doe", "track" : "01", "title" : "Introduction", "selector" : "jdoe/analysis/01 - Introduction.mp3" }
    { "_id" : ObjectId("57b7787de138236271ac5bd6"), "album" : "Analysis of non-establishment systems for extensive compliance systems", "hash" : "b/Xhi4lRoqFdMW4BvbyT3Q==", "author" : "John Doe", "track" : "06", "title" : "5 Tension in Distinction", "selector" : "jdoe/analysis/06 - 5 Tension in Distinction.mp3" }
    { "_id" : ObjectId("57b7787ee138236271ac5bd8"), "album" : "Analysis of non-establishment systems for extensive compliance systems", "hash" : "BWOeeMm/mzIR2vFtALjR8A==", "author" : "John Doe", "track" : "02", "title" : "1 Locke on the Analysis of the Establishments", "selector" : "jdoe/analysis/02 - 1 Locke on the Analysis of the Establishments.mp3" }
    { "_id" : ObjectId("57b77880e138236271ac5bda"), "album" : "Analysis of non-establishment systems for extensive compliance systems", "hash" : "8a/T/S2VVxh7oy6P7lCBbQ==", "author" : "Jane Smith", "track" : "03", "title" : "2 The Government Controversies", "selector" : "jdoe/analysis/03 - 2 The Government Controversies.mp3" }
    { "_id" : ObjectId("57b77885e138236271ac5bde"), "album" : "Analysis of non-establishment systems for extensive compliance systems", "hash" : "RcnON7bm4Q94Pm+y8pDd4Q==", "author" : "John Doe", "track" : "04", "title" : "3 The Intellectual Shape of the Compliance Debates", "selector" : "jdoe/analysis/04 - 3 The Intellectual Shape of the Compliance Debates.mp3" }
    { "_id" : ObjectId("57b77888e138236271ac5be0"), "album" : "Analysis of non-establishment systems for extensive compliance systems", "hash" : "QMHU1SpOQ3e/DmX8Pl/IyQ==", "author" : "John Doe", "track" : "05", "title" : "4 Identity, Distinction, or Tension in Non-Establishment Language", "selector" : "jdoe/analysis/05 - 4 Identity, Distinction, or Tension in Non-Establishment Language.mp3" }
    { "_id" : ObjectId("57b7788ce138236271ac5be2"), "album" : "Analysis of non-establishment systems for extensive compliance systems", "hash" : "vy7z4x+u0jhPJppc1GEHqg==", "author" : "John Doe", "track" : "07", "title" : "6 The Irreducible Extensiveness of Systems", "selector" : "jdoe/analysis/07 - 6 The Irreducible Extensiveness of Systems.mp3" }
    >
    
