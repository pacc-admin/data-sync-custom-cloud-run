
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import mssql,big_query

database = ['IPOSS5WINE','IPOSSBGN']
schema='IPOS_SALE'
table_name='dm_item'

print('delete current table')
big_query.bq_delete(schema,table_id=table_name)

for database_name in database:
    query_string = '''
                    with item_grouped as (
                        select
                             item_type_id,
                             item_type_name,
                        	 row_number() over (partition by item_type_id order by item_type_name desc) as rn
                        
                        from '''+database_name+'''.dbo.dm_item_type
                        where active = 1
                    ),
                    
                    item_cat as (
                        select distinct
                             item_class_id,
                             item_class_name
                        
                        from '''+database_name+'''.dbo.dm_item_class
                    )

                    select  
                        item.*,
                        item_cat.item_class_name as item_category,
                        item_grouped.item_type_name as item_group,
                        '''+"'"+database_name+"'"+''' as data_source
                    
                    from '''+database_name+'.dbo.'+table_name+''' item
                    left join item_cat
                        on item.item_class_id = item_cat.item_class_id
                    left join item_grouped
                        on item.item_type_id = item_grouped.item_type_id
                        and rn = 1
                    '''
    condition="data_source='"+database_name+"'"
    mssql.full_refresh_sale(query_string,schema,table_name,condition=condition)
