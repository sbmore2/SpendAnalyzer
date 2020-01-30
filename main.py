import parser
import categorize


if __name__ == "__main__":
    df = parser.parse_bank_statement('SampleStatements/20170323-statements-6082-.pdf')
    categorize.categorize(df)
    parser.save_categorized_statement(df, 'SampleStatements/20170323-statements-6082-.csv')
    categorize.create_pie_chart(df)
    categorize.create_pie_chart(parser.read_categorized_statement('train.csv'))

