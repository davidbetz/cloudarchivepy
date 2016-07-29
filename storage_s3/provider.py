from general.debug import kwlog, log, logline, logargs

class S3AssetProvider():
    def check(self, area, selector, hash):
        if area == None:
            return asset_status_code.error

        storageConfig = StorageConfig.Get(area)
        credentials = new BasicAWSCredentials(storageConfig.Key1, storageConfig.Key2)

        area = area.lower()

        using (var client = new AmazonS3Client(credentials, RegionEndpoint.USEast1))

            bucketName = storageConfig.Name
            key = area + "/" + selector
            request = new GetObjectMetadataRequest

                BucketName = bucketName,
                Key = key


            fi = new S3FileInfo(client, bucketName, key)
            if (!fi.Exists)

                return asset_status_code.not_found


            response = client.GetObjectMetadataAsync(request)

            storedHash = response.Metadata["x-amz-meta-content-md5"]
            if (string.IsNullOrEmpty(storedHash))

                return asset_status_code.not_found


            return storedHash.Equals(hash) ? asset_status_code.Same : asset_status_code.Different

    def stream(self, area, selector):

        if area == None:

            return null

        storageConfig = StorageConfig.Get(area)
        credentials = new BasicAWSCredentials(storageConfig.Key1, storageConfig.Key2)

        area = area.lower()

        using (var client = new AmazonS3Client(credentials, RegionEndpoint.USEast1))

            request = new GetObjectRequest

                BucketName = storageConfig.Name,
                Key = area + "/" + selector

            using (var response = client.GetObject(request))
                return Task.FromResult(new Tuple<string, Stream>(response.Headers["ContentType"], response.ResponseStream))

    def read(self, area, selector):
        if area == None:
            return null

        storageConfig = StorageConfig.Get(area)
        credentials = new BasicAWSCredentials(storageConfig.Key1, storageConfig.Key2)

        area = area.lower()

        using (var client = new AmazonS3Client(credentials, RegionEndpoint.USEast1))

            request = new GetObjectRequest

                BucketName = storageConfig.Name,
                Key = area + "/" + selector

            using (var response = client.GetObject(request))
                return Task.FromResult(StreamConverter.GetStreamByteArray(response.ResponseStream))

    def get_url(self, area, selector):
        if area == None:
            return null

        storageConfig = StorageConfig.Get(area)
        credentials = new BasicAWSCredentials(storageConfig.Key1, storageConfig.Key2)

        area = area.lower()

        using (var client = new AmazonS3Client(credentials, RegionEndpoint.USEast1))
            request = new GetPreSignedUrlRequest

                BucketName = storageConfig.Name,
                Key = area + "/" + selector,
                Expires = DateTime.Now.AddMinutes(30)

            return Task.FromResult(client.GetPreSignedURL(request))

    # S3 buckets are not like Azure containers; S3 buckets are like Azure accounts; thus, S3 doesn't use area
    def ensure_access(self, area)
        storageConfig = StorageConfig.Get(area)
        credentials = new BasicAWSCredentials(storageConfig.Key1, storageConfig.Key2)

        using (var client = new AmazonS3Client(credentials, RegionEndpoint.USEast1))

            configuration = new CORSConfiguration

                Rules = new List<CORSRule>

                    new CORSRule

                        Id = "all",
                        AllowedMethods = new List<string> "GET",
                        AllowedOrigins = new List<string> "*",
                        MaxAgeSeconds = 3000




            request = new PutCORSConfigurationRequest

                BucketName = storageConfig.Name,
                Configuration = configuration


            await client.PutCORSConfigurationAsync(request)



    def update(self, area, selector, contentType, buffer)
        if area == None:
            return null

        storageConfig = StorageConfig.Get(area)
        credentials = new BasicAWSCredentials(storageConfig.Key1, storageConfig.Key2)

        area = area.lower()

        hash = QuickHash.Hash(buffer, HashMethod.SHA256)
        using (var client = new AmazonS3Client(credentials, RegionEndpoint.USEast1))

            putObjectRequest = new PutObjectRequest

                BucketName = storageConfig.Name,
                Key = area + "/" + selector,
                InputStream = new MemoryStream(buffer),
                ContentType = contentType,
                Metadata =  ["Content-MD5"] = hash ,
                CannedACL = S3CannedACL.PublicRead


            await client.PutObjectAsync(putObjectRequest)

        return hash

    def clean_selector(self, selector):
        return selector.Replace("/", "_").Replace(".", "=")