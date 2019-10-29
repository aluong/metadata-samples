SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[tbl_datasets](
	[clm_int_id] [int] IDENTITY(1,1) NOT NULL,
	[clm_int_lineage_request_id] [int] NOT NULL,
	[clm_varchar_dataset] [varchar](256) NOT NULL,
	[clm_varchar_type] [varchar](256) NOT NULL,
	[clm_varchar_azure_resource] [varchar](256) NOT NULL,
	[clm_varchar_direction] [varchar](256) NOT NULL,
 CONSTRAINT [PK_tbl_datasets] PRIMARY KEY CLUSTERED 
(
	[clm_int_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[tbl_lineage_request](
	[clm_int_id] [int] IDENTITY(1,1) NOT NULL,
	[clm_varchar_execution_start_time] [datetime2](7) NOT NULL,
	[clm_varchar_execution_end_time] [datetime2](7) NOT NULL,
	[clm_varchar_datafactory_name] [varchar](256) NOT NULL,
	[clm_varchar_pipeline_name] [varchar](256) NOT NULL,
	[clm_varchar_activity_name] [varchar](256) NOT NULL,
 CONSTRAINT [PK_tbl_lineage_request] PRIMARY KEY CLUSTERED 
(
	[clm_int_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[tbl_datasets]  WITH CHECK ADD  CONSTRAINT [FK_tbl_datasets_tbl_lineage_request] FOREIGN KEY([clm_int_lineage_request_id])
REFERENCES [dbo].[tbl_lineage_request] ([clm_int_id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[tbl_datasets] CHECK CONSTRAINT [FK_tbl_datasets_tbl_lineage_request]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[sp_create_lineage]
(
    @execution_start_time varchar(256),
    @execution_end_time varchar(256),

    @datafactory_name varchar(256),
    @pipeline_name varchar(256),
    @activity_name varchar(256),

    @source_dataset varchar(256),
    @source_type varchar(256),
    @source_azure_resource varchar(256),

    @destination_dataset varchar(256),
    @destination_type varchar(256),
    @destination_azure_resource varchar(256)
)
AS
BEGIN
    SET NOCOUNT ON

	INSERT INTO tbl_lineage_request (clm_varchar_execution_start_time, clm_varchar_execution_end_time, clm_varchar_datafactory_name, clm_varchar_pipeline_name, clm_varchar_activity_name)
	values (@execution_start_time, @execution_end_time, @datafactory_name, @pipeline_name, @activity_name)

	DECLARE @requestId AS int
	SET @requestId = @@IDENTITY

	INSERT INTO tbl_datasets 
	(clm_int_lineage_request_id, clm_varchar_direction, clm_varchar_dataset, clm_varchar_type, clm_varchar_azure_resource)
	values (@requestId, 'source', @source_dataset, @source_type, @source_azure_resource)

	INSERT INTO tbl_datasets 
	(clm_int_lineage_request_id, clm_varchar_direction, clm_varchar_dataset, clm_varchar_type, clm_varchar_azure_resource)
	values (@requestId, 'destination', @destination_dataset, @destination_type, @destination_azure_resource)
END
GO